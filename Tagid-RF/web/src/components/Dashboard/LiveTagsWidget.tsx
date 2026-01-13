import { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { useWebSocket } from '@/hooks/useWebSocket';
import { slideInUp } from '@/styles/animations';

const WidgetContainer = styled.div`
  background: ${theme.colors.surface};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  box-shadow: ${theme.shadows.md};
  margin-bottom: ${theme.spacing.xl};
  animation: ${slideInUp} 0.5s ease-out;
  border: 1px solid ${theme.colors.border};
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h2`
  font-size: ${theme.typography.fontSize['xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};

  &::before {
    content: '📡';
    font-size: 1.2em;
  }
`;

const StatusBadge = styled.span<{ $status: string }>`
  font-size: ${theme.typography.fontSize.xs};
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.full};
  background: ${props => props.$status === 'connected' ? theme.colors.success + '20' : theme.colors.error + '20'};
  color: ${props => props.$status === 'connected' ? theme.colors.success : theme.colors.error};
  font-weight: ${theme.typography.fontWeight.medium};
  display: flex;
  align-items: center;
  gap: 6px;

  &::before {
    content: '';
    display: block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    animation: ${props => props.$status === 'connected' ? 'pulse 2s infinite' : 'none'};
  }

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const StatsRow = styled.div`
  display: flex;
  gap: ${theme.spacing.xl};
  margin-bottom: ${theme.spacing.lg};
  padding-bottom: ${theme.spacing.lg};
  border-bottom: 1px solid ${theme.colors.border};
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
`;

const StatValue = styled.span`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
`;

const StatLabel = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const TagList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
  max-height: 300px;
  overflow-y: auto;
  padding-right: ${theme.spacing.xs};

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: ${theme.colors.backgroundAlt};
    border-radius: 3px;
  }
  &::-webkit-scrollbar-thumb {
    background: ${theme.colors.gray[300]};
    border-radius: 3px;
  }
`;

const TagItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${theme.spacing.md};
  background: ${theme.colors.backgroundAlt};
  border-radius: ${theme.borderRadius.md};
  transition: all 0.2s;
  border-left: 3px solid ${theme.colors.primary};

  &:hover {
    background: ${theme.colors.gray[100]};
    transform: translateX(2px);
  }
  
  animation: ${slideInUp} 0.3s ease-out;
`;

const TagEPC = styled.span`
  font-family: monospace;
  font-size: ${theme.typography.fontSize.md};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const TagMeta = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const RSSI = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  font-family: monospace;
`;

const Time = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.gray[500]};
`;

interface TagEvent {
    epc: string;
    rssi?: number;
    timestamp: string;
    reader_ip?: string;
}

export function LiveTagsWidget() {
    const [tags, setTags] = useState<TagEvent[]>([]);
    const [stats, setStats] = useState({ total: 0, unique: 0 });
    const uniqueEpcs = useRef(new Set<string>());

    // WebSocket Connection
    const { status } = useWebSocket({
        url: '/ws/rfid', // Assuming proxy forwards /ws to backend
        onMessage: (message) => {
            if (message.type === 'tag_scanned') {
                handleNewTag(message.data);
            }
        },
    });

    // Handle new tag
    const handleNewTag = (tag: TagEvent) => {
        setTags(prev => {
            const newTags = [tag, ...prev].slice(0, 50); // Keep last 50
            return newTags;
        });

        uniqueEpcs.current.add(tag.epc);
        setStats(prev => ({
            total: prev.total + 1,
            unique: uniqueEpcs.current.size
        }));
    };

    // Initial fetch of recent tags
    useEffect(() => {
        fetch('/api/v1/tags/live/recent?count=10')
            .then(res => res.json())
            .then(data => {
                if (data.tags) {
                    setTags(data.tags);
                    // Update unique set
                    data.tags.forEach((t: TagEvent) => uniqueEpcs.current.add(t.epc));
                }
                if (data.stats) {
                    setStats({
                        total: data.stats.total_scans,
                        unique: data.stats.unique_epcs
                    });
                }
            })
            .catch(err => console.error('Failed to fetch recent tags:', err));
    }, []);

    return (
        <WidgetContainer>
            <Header>
                <Title>סריקות בזמן אמת</Title>
                <StatusBadge $status={status}>
                    {status === 'connected' ? 'מחובר לקורא' : 'מנותק'}
                </StatusBadge>
            </Header>

            <StatsRow>
                <StatItem>
                    <StatValue>{stats.total}</StatValue>
                    <StatLabel>סה"כ סריקות</StatLabel>
                </StatItem>
                <StatItem>
                    <StatValue>{stats.unique}</StatValue>
                    <StatLabel>תגים ייחודיים</StatLabel>
                </StatItem>
                <StatItem>
                    <StatValue>{tags.length}</StatValue>
                    <StatLabel>מוצגים כעת</StatLabel>
                </StatItem>
            </StatsRow>

            <TagList>
                {tags.length > 0 ? (
                    tags.map((tag, index) => (
                        <TagItem key={`${tag.epc}-${index}`}>
                            <TagEPC>{tag.epc}</TagEPC>
                            <TagMeta>
                                {tag.rssi && <RSSI>{tag.rssi} dBm</RSSI>}
                                <Time>{new Date(tag.timestamp).toLocaleTimeString()}</Time>
                            </TagMeta>
                        </TagItem>
                    ))
                ) : (
                    <div style={{ textAlign: 'center', padding: '20px', color: theme.colors.textSecondary }}>
                        ממתין לסריקות...
                    </div>
                )}
            </TagList>
        </WidgetContainer>
    );
}
