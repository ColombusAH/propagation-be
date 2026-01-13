import { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { LiveTagsWidget } from '@/components/Dashboard/LiveTagsWidget';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

// Professional color palette
const colors = {
  primary: '#1e40af',      // Deep blue
  primaryLight: '#3b82f6',
  secondary: '#0f766e',    // Teal
  accent: '#7c3aed',       // Purple
  success: '#059669',
  warning: '#d97706',
  danger: '#dc2626',
  dark: '#1e293b',
  slate: '#475569',
  light: '#f1f5f9',
};

// Animations
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

// Styled Components
const Container = styled.div`
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background: #f8fafc;
  min-height: 100vh;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  animation: ${fadeIn} 0.4s ease-out;
`;

const HeaderLeft = styled.div``;

const Title = styled.h1`
  font-size: 1.75rem;
  font-weight: 700;
  color: ${colors.dark};
  margin: 0;
`;

const Subtitle = styled.p`
  font-size: 0.95rem;
  color: ${colors.slate};
  margin: 0.25rem 0 0 0;
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const RoleBadge = styled.span`
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  background: ${colors.primary};
  color: white;
`;

const LogoutButton = styled.button`
  padding: 0.4rem 0.75rem;
  background: white;
  color: ${colors.slate};
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
  }
`;

// Quick Actions - Professional icons
const QuickActionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
  animation: ${fadeIn} 0.5s ease-out;
  
  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
`;

const QuickActionCard = styled.button<{ $color: string }>`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: right;
  
  &:hover {
    border-color: ${props => props.$color};
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transform: translateY(-2px);
  }
`;

const ActionIcon = styled.div<{ $color: string }>`
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: ${props => props.$color}15;
  color: ${props => props.$color};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
`;

const ActionText = styled.div`
  flex: 1;
`;

const ActionLabel = styled.div`
  font-size: 0.95rem;
  font-weight: 600;
  color: ${colors.dark};
`;

const ActionDesc = styled.div`
  font-size: 0.8rem;
  color: ${colors.slate};
  margin-top: 2px;
`;

// Stats Grid
const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
  animation: ${fadeIn} 0.6s ease-out;
  
  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
`;

const StatCard = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
`;

const StatLabel = styled.div`
  font-size: 0.85rem;
  color: ${colors.slate};
  margin-bottom: 0.5rem;
`;

const StatValue = styled.div`
  font-size: 1.75rem;
  font-weight: 700;
  color: ${colors.dark};
`;

const StatTrend = styled.span<{ $positive: boolean }>`
  font-size: 0.8rem;
  font-weight: 500;
  color: ${props => props.$positive ? colors.success : colors.danger};
  display: inline-flex;
  align-items: center;
  gap: 2px;
  margin-top: 0.5rem;
`;

// Content Grid
const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  animation: ${fadeIn} 0.7s ease-out;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
`;

const CardTitle = styled.h2`
  font-size: 1rem;
  font-weight: 600;
  color: ${colors.dark};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ViewAllLink = styled.button`
  background: none;
  border: none;
  color: ${colors.primaryLight};
  font-size: 0.85rem;
  cursor: pointer;
  
  &:hover {
    text-decoration: underline;
  }
`;

// Transactions List
const TransactionList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const TransactionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  
  &:hover {
    background: #f1f5f9;
  }
`;

const TransactionInfo = styled.div``;

const TransactionId = styled.div`
  font-weight: 600;
  font-size: 0.9rem;
  color: ${colors.dark};
`;

const TransactionTime = styled.div`
  font-size: 0.8rem;
  color: ${colors.slate};
`;

const TransactionAmount = styled.span`
  font-size: 1rem;
  font-weight: 700;
  color: ${colors.success};
`;

// Reader Status Card - Professional dark theme
const ReaderCard = styled(Card)`
  background: linear-gradient(135deg, ${colors.dark}, #334155);
  border: none;
  color: white;
`;

const ReaderHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const ReaderTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: white;
`;

const StatusIndicator = styled.div<{ $active: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: ${props => props.$active ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'};
  border-radius: 20px;
  font-size: 0.8rem;
  color: ${props => props.$active ? '#34d399' : '#f87171'};
`;

const StatusDot = styled.span<{ $active: boolean }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.$active ? '#34d399' : '#f87171'};
`;

const ReaderInfo = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 1rem 0;
`;

const InfoItem = styled.div``;

const InfoLabel = styled.div`
  font-size: 0.75rem;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const InfoValue = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin-top: 2px;
`;

const ReaderButton = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 0.5rem;
  
  ${props => props.$variant === 'primary' ? `
    background: ${colors.success};
    color: white;
    
    &:hover {
      background: #047857;
    }
  ` : `
    background: rgba(255,255,255,0.1);
    color: white;
    
    &:hover {
      background: rgba(255,255,255,0.15);
    }
  `}
`;

export function DashboardPage() {
  const { userRole, token, logout } = useAuth();
  const navigate = useNavigate();

  const [readerStatus, setReaderStatus] = useState({
    is_connected: false,
    is_scanning: false,
    reader_ip: '192.168.1.200',
    reader_port: 2023,
  });

  const [stats] = useState({
    revenue: 15420,
    sales: 48,
    items: 156,
    avgTransaction: 321,
  });

  const [recentTransactions] = useState([
    { id: 'TXN-001', amount: 450, time: '10:30' },
    { id: 'TXN-002', amount: 280, time: '11:15' },
    { id: 'TXN-003', amount: 620, time: '12:00' },
    { id: 'TXN-004', amount: 150, time: '13:45' },
  ]);

  const getRoleName = (role: string) => {
    switch (role) {
      case 'ADMIN': return 'מנהל מערכת';
      case 'MANAGER': return 'מנהל';
      case 'CASHIER': return 'קופאי';
      default: return 'משתמש';
    }
  };

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/v1/rfid-scan/status');
        if (response.ok) {
          const data = await response.json();
          setReaderStatus(data);
        }
      } catch (e) {
        // Silent fail
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStartScan = async () => {
    try {
      await fetch('/api/v1/rfid-scan/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });
      setReaderStatus(prev => ({ ...prev, is_scanning: true }));
    } catch (e) {
      console.error('Failed to start scan');
    }
  };

  const quickActions = [
    {
      icon: '🏷️',
      label: 'סריקת תגים',
      desc: 'סנכרון QR ↔ UHF',
      color: colors.primary,
      onClick: () => navigate('/tag-mapping')
    },
    {
      icon: '📡',
      label: 'הגדרות קורא',
      desc: 'עוצמה, רשת, ממסרים',
      color: colors.secondary,
      onClick: () => navigate('/reader-settings')
    },
    {
      icon: '📊',
      label: 'דוחות עסקאות',
      desc: 'צפייה ויצוא',
      color: colors.accent,
      onClick: () => navigate('/transactions')
    },
    {
      icon: '👥',
      label: 'ניהול משתמשים',
      desc: 'הרשאות ותפקידים',
      color: colors.warning,
      onClick: () => navigate('/users')
    },
  ];

  return (
    <Layout>
      <Container>
        {/* Header */}
        <Header>
          <HeaderLeft>
            <Title>לוח בקרה</Title>
            <Subtitle>סקירת מערכת • {new Date().toLocaleDateString('he-IL')}</Subtitle>
          </HeaderLeft>
          <HeaderRight>
            <RoleBadge>{getRoleName(userRole || '')}</RoleBadge>
            <LogoutButton onClick={logout}>התנתק</LogoutButton>
          </HeaderRight>
        </Header>

        {/* Quick Actions */}
        <QuickActionsGrid>
          {quickActions.map((action, index) => (
            <QuickActionCard
              key={index}
              $color={action.color}
              onClick={action.onClick}
            >
              <ActionIcon $color={action.color}>{action.icon}</ActionIcon>
              <ActionText>
                <ActionLabel>{action.label}</ActionLabel>
                <ActionDesc>{action.desc}</ActionDesc>
              </ActionText>
            </QuickActionCard>
          ))}
        </QuickActionsGrid>

        {/* Stats */}
        <StatsGrid>
          <StatCard>
            <StatLabel>הכנסות היום</StatLabel>
            <StatValue>₪{stats.revenue.toLocaleString()}</StatValue>
            <StatTrend $positive={true}>↑ 12% מאתמול</StatTrend>
          </StatCard>
          <StatCard>
            <StatLabel>מכירות</StatLabel>
            <StatValue>{stats.sales}</StatValue>
            <StatTrend $positive={true}>↑ 8% מאתמול</StatTrend>
          </StatCard>
          <StatCard>
            <StatLabel>פריטים נמכרו</StatLabel>
            <StatValue>{stats.items}</StatValue>
            <StatTrend $positive={false}>↓ 5% מאתמול</StatTrend>
          </StatCard>
          <StatCard>
            <StatLabel>ממוצע עסקה</StatLabel>
            <StatValue>₪{stats.avgTransaction}</StatValue>
            <StatTrend $positive={true}>↑ 15% מאתמול</StatTrend>
          </StatCard>
        </StatsGrid>

        {/* Content */}
        <ContentGrid>
          {/* Transactions */}
          <Card>
            <CardHeader>
              <CardTitle>💰 עסקאות אחרונות</CardTitle>
              <ViewAllLink onClick={() => navigate('/transactions')}>
                צפה בכל →
              </ViewAllLink>
            </CardHeader>
            <TransactionList>
              {recentTransactions.map(txn => (
                <TransactionItem key={txn.id}>
                  <TransactionInfo>
                    <TransactionId>{txn.id}</TransactionId>
                    <TransactionTime>היום, {txn.time}</TransactionTime>
                  </TransactionInfo>
                  <TransactionAmount>+₪{txn.amount}</TransactionAmount>
                </TransactionItem>
              ))}
            </TransactionList>
          </Card>

          {/* Reader Status */}
          <ReaderCard>
            <ReaderHeader>
              <ReaderTitle>📡 קורא RFID</ReaderTitle>
              <StatusIndicator $active={readerStatus.is_connected}>
                <StatusDot $active={readerStatus.is_connected} />
                {readerStatus.is_connected ? 'מחובר' : 'לא מחובר'}
              </StatusIndicator>
            </ReaderHeader>

            <ReaderInfo>
              <InfoItem>
                <InfoLabel>כתובת IP</InfoLabel>
                <InfoValue>{readerStatus.reader_ip}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>פורט</InfoLabel>
                <InfoValue>{readerStatus.reader_port}</InfoValue>
              </InfoItem>
            </ReaderInfo>

            <ReaderButton $variant="primary" onClick={handleStartScan}>
              {readerStatus.is_connected
                ? (readerStatus.is_scanning ? '⏹ עצור סריקה' : '▶ התחל סריקה')
                : '🔌 התחבר לקורא'}
            </ReaderButton>
            <ReaderButton onClick={() => navigate('/reader-settings')}>
              ⚙️ הגדרות מתקדמות
            </ReaderButton>
          </ReaderCard>
        </ContentGrid>

        {/* Live Tags Widget */}
        <div style={{ marginTop: '1.5rem' }}>
          <LiveTagsWidget />
        </div>
      </Container>
    </Layout>
  );
}
