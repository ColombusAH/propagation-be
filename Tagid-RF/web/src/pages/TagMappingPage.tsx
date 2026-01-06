import { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { QRCodeSVG } from 'qrcode.react';
import { Layout } from '@/components/Layout';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';
import { useWebSocket } from '@/hooks/useWebSocket';

// Types
interface TagMapping {
    id: string;
    epc: string;
    encrypted_qr: string;
    epc_hash: string | null;
    product_id: string | null;
    container_id: string | null;
    is_active: boolean;
}

interface ScannedTag {
    tag_id: number;
    epc: string;
    rssi: number;
    antenna_port: number;
    timestamp: string;
    is_mapped: boolean;
    target_qr: string | null;
}

// API base URL
const API_BASE = '/api/v1/tag-mapping';

// Styled Components
const Container = styled.div`
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
`;

const Title = styled.h1`
  font-size: 1.8rem;
  font-weight: 700;
  color: ${theme.colors.text};
  margin: 0;
`;

const Card = styled.div`
  background: ${theme.colors.surface};
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
`;

const CardTitle = styled.h2`
  font-size: 1.2rem;
  font-weight: 600;
  color: ${theme.colors.text};
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-size: 0.9rem;
  font-weight: 500;
  color: ${theme.colors.textSecondary};
`;

const Input = styled.input`
  padding: 0.875rem 1rem;
  border: 2px solid ${theme.colors.border};
  border-radius: 12px;
  font-size: 1rem;
  background: ${theme.colors.background};
  color: ${theme.colors.text};
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}20;
  }
  
  &::placeholder {
    color: ${theme.colors.textSecondary};
  }
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  ${({ variant = 'primary' }) => {
        switch (variant) {
            case 'secondary':
                return `
          background: ${theme.colors.surface};
          color: ${theme.colors.text};
          border: 2px solid ${theme.colors.border};
          &:hover { background: ${theme.colors.background}; }
        `;
            case 'danger':
                return `
          background: ${theme.colors.error};
          color: white;
          &:hover { opacity: 0.9; }
        `;
            default:
                return `
          background: ${theme.colors.primary};
          color: white;
          &:hover { opacity: 0.9; transform: translateY(-1px); }
        `;
        }
    }}
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
`;

const MappingCard = styled.div`
  background: ${theme.colors.background};
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid ${theme.colors.border};
  
  &:hover {
    border-color: ${theme.colors.primary};
  }
`;

const EpcCode = styled.code`
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  background: ${theme.colors.surface};
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  color: ${theme.colors.primary};
  word-break: break-all;
`;

const QrContainer = styled.div`
  display: flex;
  justify-content: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  margin: 1rem 0;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const SmallButton = styled.button`
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &.copy {
    background: ${theme.colors.secondary};
    color: white;
  }
  &.delete {
    background: ${theme.colors.error}20;
    color: ${theme.colors.error};
  }
  &.connect {
    background: ${theme.colors.success + '20'};
    color: ${theme.colors.success};
    border: 1px solid ${theme.colors.success};
  }
  &.disconnect {
    background: ${theme.colors.error + '20'};
    color: ${theme.colors.error};
    border: 1px solid ${theme.colors.error};
  }
  
  &:hover {
    opacity: 0.8;
  }
`;

const StatusBadge = styled.span<{ active: boolean }>`
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  background: ${({ active }) => active ? theme.colors.success + '20' : theme.colors.error + '20'};
  color: ${({ active }) => active ? theme.colors.success : theme.colors.error};
`;

const Message = styled.div<{ type: 'success' | 'error' }>`
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  background: ${({ type }) => type === 'success' ? theme.colors.success + '20' : theme.colors.error + '20'};
  color: ${({ type }) => type === 'success' ? theme.colors.success : theme.colors.error};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem;
  color: ${theme.colors.textSecondary};
`;

const VerifySection = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const VerifyResult = styled.div<{ match: boolean }>`
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
  background: ${({ match }) => match ? theme.colors.success + '20' : theme.colors.error + '20'};
  color: ${({ match }) => match ? theme.colors.success : theme.colors.error};
`;

const LiveParams = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: ${theme.colors.background};
  border-radius: 12px;
`;

const ToggleSwitch = styled.label`
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  span {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 34px;
    
    &:before {
      position: absolute;
      content: "";
      height: 16px;
      width: 16px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
  }
  
  input:checked + span {
    background-color: ${theme.colors.primary};
  }
  
  input:checked + span:before {
    transform: translateX(26px);
  }
`;

const LiveTagRow = styled.div<{ newItem: boolean }>`
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  padding: 0.75rem;
  border-bottom: 1px solid ${theme.colors.border};
  align-items: center;
  animation: ${({ newItem }) => newItem ? 'highlight 1s ease-out' : 'none'};
  transition: background-color 0.5s;

  @keyframes highlight {
    0% { background-color: ${theme.colors.primary}40; }
    100% { background-color: transparent; }
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

export function TagMappingPage() {
    const { t } = useTranslation();
    const [mappings, setMappings] = useState<TagMapping[]>([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    // Live Scan State
    const [liveTags, setLiveTags] = useState<ScannedTag[]>([]);
    const [autoGenerate, setAutoGenerate] = useState(false);
    const [isWsConnected, setIsWsConnected] = useState(false);

    // Create form state
    const [newEpc, setNewEpc] = useState('');
    const [productId, setProductId] = useState('');
    const [creating, setCreating] = useState(false);

    // Verify form state
    const [verifyEpc, setVerifyEpc] = useState('');
    const [verifyQr, setVerifyQr] = useState('');
    const [verifyResult, setVerifyResult] = useState<{ match: boolean; message: string } | null>(null);
    const [verifying, setVerifying] = useState(false);

    // WebSocket
    const { status, connect, disconnect } = useWebSocket({
        url: '/ws/rfid',
        autoConnect: true,
        onMessage: (msg) => {
            if (msg.type === 'tag_scanned') {
                handleTagScanned(msg.data);
            }
        }
    });

    useEffect(() => {
        setIsWsConnected(status === 'connected');
    }, [status]);

    useEffect(() => {
        loadMappings();
    }, []);

    const handleTagScanned = async (tag: ScannedTag) => {
        setLiveTags(prev => {
            // Keep last 10 tags, update if exists, push if new
            const exists = prev.find(t => t.epc === tag.epc);
            if (exists) {
                // Return new array with updated timestamp/rssi but move to top?
                // Or just update in place. Let's move to top.
                const filtered = prev.filter(t => t.epc !== tag.epc);
                return [tag, ...filtered].slice(0, 10);
            }
            return [tag, ...prev].slice(0, 10);
        });

        // Auto Generate Logic
        if (autoGenerate && !tag.is_mapped) {
            // Check if we are already creating this one to avoid race conditions
            // Simple approach: trigger creation
            await createMappingForTag(tag.epc);
        }
    };

    const createMappingForTag = async (epc: string) => {
        try {
            console.log('Auto-generating mapping for:', epc);
            const response = await fetch(`${API_BASE}/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    epc: epc,
                    product_id: 'auto-gen-' + Date.now() // Optional: remove if you want null
                })
            });

            if (response.ok) {
                const newMapping = await response.json();
                setMappings(prev => [newMapping, ...prev]);
                // Update live tag status manually in list
                setLiveTags(prev => prev.map(t =>
                    t.epc === epc
                        ? { ...t, is_mapped: true, target_qr: newMapping.encrypted_qr }
                        : t
                ));
            }
        } catch (error) {
            console.error('Auto-generation failed', error);
        }
    };

    const loadMappings = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE}/list`);
            if (response.ok) {
                const data = await response.json();
                setMappings(data);
            }
        } catch (error) {
            console.error('Failed to load mappings:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newEpc.trim()) return;

        try {
            setCreating(true);
            const response = await fetch(`${API_BASE}/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    epc: newEpc.trim(),
                    product_id: productId.trim() || null
                })
            });

            if (response.ok) {
                const newMapping = await response.json();
                setMappings(prev => [newMapping, ...prev]);
                setNewEpc('');
                setProductId('');
                setMessage({ type: 'success', text: '🔐 מיפוי מוצפן נוצר בהצלחה!' });
            } else {
                const error = await response.json();
                setMessage({ type: 'error', text: error.detail || 'שגיאה ביצירת מיפוי' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'שגיאת רשת' });
        } finally {
            setCreating(false);
            setTimeout(() => setMessage(null), 3000);
        }
    };

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!verifyEpc.trim() || !verifyQr.trim()) return;

        try {
            setVerifying(true);
            const response = await fetch(`${API_BASE}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    epc: verifyEpc.trim(),
                    qr_code: verifyQr.trim()
                })
            });

            if (response.ok) {
                const result = await response.json();
                setVerifyResult({ match: result.match, message: result.message });
            }
        } catch (error) {
            setVerifyResult({ match: false, message: 'שגיאת רשת' });
        } finally {
            setVerifying(false);
        }
    };

    const handleDelete = async (mappingId: string) => {
        if (!confirm('האם למחוק את המיפוי?')) return;

        try {
            const response = await fetch(`${API_BASE}/${mappingId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                setMappings(prev => prev.filter(m => m.id !== mappingId));
                setMessage({ type: 'success', text: 'מיפוי נמחק' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'שגיאה במחיקה' });
        }
        setTimeout(() => setMessage(null), 3000);
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setMessage({ type: 'success', text: '📋 הועתק!' });
        setTimeout(() => setMessage(null), 2000);
    };

    return (
        <Layout>
            <Container>
                <Header>
                    <Title>🔐 סנכרון QR ↔ UHF Tags</Title>
                    <div>
                        Status: <StatusBadge active={isWsConnected}>{isWsConnected ? 'Connected' : 'Disconnected'}</StatusBadge>
                    </div>
                </Header>

                {message && (
                    <Message type={message.type}>{message.text}</Message>
                )}

                {/* Live Scan & Auto Generate */}
                <Card>
                    <CardTitle>📡 סריקה חיה & יצירה אוטומטית</CardTitle>
                    <LiveParams>
                        <div style={{ flex: 1 }}>
                            <strong>יצירה אוטומטית של QR:</strong>
                            <div style={{ fontSize: '0.85rem', color: theme.colors.textSecondary }}>
                                אם מופעל, כל תג חדש שנסרק יקבל מיפוי אוטומטית
                            </div>
                        </div>
                        <ToggleSwitch>
                            <input
                                type="checkbox"
                                checked={autoGenerate}
                                onChange={(e) => setAutoGenerate(e.target.checked)}
                            />
                            <span></span>
                        </ToggleSwitch>
                    </LiveParams>

                    {liveTags.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '1rem', color: theme.colors.textSecondary }}>
                            ממתין לסריקת תגים...
                        </div>
                    ) : (
                        <div>
                            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', padding: '0.5rem', fontWeight: 'bold' }}>
                                <div>EPC</div>
                                <div>RSSI</div>
                                <div>Status</div>
                                <div>QR</div>
                            </div>
                            {liveTags.map((tag) => (
                                <LiveTagRow key={tag.epc} newItem={true}>
                                    <EpcCode>{tag.epc}</EpcCode>
                                    <div>{tag.rssi} dBm</div>
                                    <div>
                                        <StatusBadge active={tag.is_mapped}>
                                            {tag.is_mapped ? 'Mapped' : 'New'}
                                        </StatusBadge>
                                    </div>
                                    <div>
                                        {tag.target_qr && (
                                            <span
                                                style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                                                onClick={() => copyToClipboard(tag.target_qr!)}
                                                title="Click to copy QR string"
                                            >
                                                🔐
                                            </span>
                                        )}
                                    </div>
                                </LiveTagRow>
                            ))}
                        </div>
                    )}
                </Card>

                {/* Create New Mapping */}
                <Card>
                    <CardTitle>➕ יצירת מיפוי חדש (ידני)</CardTitle>
                    <Form onSubmit={handleCreate}>
                        <InputGroup>
                            <Label>EPC של תג UHF</Label>
                            <Input
                                type="text"
                                placeholder="E2806810000000001234"
                                value={newEpc}
                                onChange={(e) => setNewEpc(e.target.value)}
                                required
                            />
                        </InputGroup>
                        <InputGroup>
                            <Label>מזהה מוצר (אופציונלי)</Label>
                            <Input
                                type="text"
                                placeholder="product-123"
                                value={productId}
                                onChange={(e) => setProductId(e.target.value)}
                            />
                        </InputGroup>
                        <Button type="submit" disabled={creating || !newEpc.trim()}>
                            {creating ? '⏳ יוצר...' : '🔐 צור QR מוצפן'}
                        </Button>
                    </Form>
                </Card>

                {/* Verify Match */}
                <Card>
                    <CardTitle>✓ אימות התאמה</CardTitle>
                    <Form onSubmit={handleVerify}>
                        <VerifySection>
                            <InputGroup>
                                <Label>EPC</Label>
                                <Input
                                    type="text"
                                    placeholder="EPC מהתג"
                                    value={verifyEpc}
                                    onChange={(e) => setVerifyEpc(e.target.value)}
                                />
                            </InputGroup>
                            <InputGroup>
                                <Label>QR Code</Label>
                                <Input
                                    type="text"
                                    placeholder="מחרוזת ה-QR"
                                    value={verifyQr}
                                    onChange={(e) => setVerifyQr(e.target.value)}
                                />
                            </InputGroup>
                        </VerifySection>
                        <Button type="submit" variant="secondary" disabled={verifying}>
                            {verifying ? '⏳ בודק...' : '🔍 בדוק התאמה'}
                        </Button>
                    </Form>

                    {verifyResult && (
                        <VerifyResult match={verifyResult.match}>
                            {verifyResult.match ? '✅ ' : '❌ '}{verifyResult.message}
                        </VerifyResult>
                    )}
                </Card>

                {/* Existing Mappings */}
                <Card>
                    <CardTitle>📋 מיפויים קיימים ({mappings.length})</CardTitle>

                    {loading ? (
                        <EmptyState>⏳ טוען...</EmptyState>
                    ) : mappings.length === 0 ? (
                        <EmptyState>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔗</div>
                            <div>אין מיפויים עדיין</div>
                            <div style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                                צור את המיפוי הראשון למעלה
                            </div>
                        </EmptyState>
                    ) : (
                        <Grid>
                            {mappings.map((mapping) => (
                                <MappingCard key={mapping.id}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <strong>EPC:</strong>
                                        <StatusBadge active={mapping.is_active}>
                                            {mapping.is_active ? 'פעיל' : 'לא פעיל'}
                                        </StatusBadge>
                                    </div>
                                    <EpcCode>{mapping.epc}</EpcCode>

                                    <QrContainer>
                                        <QRCodeSVG
                                            value={mapping.encrypted_qr}
                                            size={120}
                                            level="M"
                                        />
                                    </QrContainer>

                                    <div style={{ fontSize: '0.75rem', color: theme.colors.textSecondary }}>
                                        QR (מוצפן): {mapping.encrypted_qr.substring(0, 30)}...
                                    </div>

                                    <ActionButtons>
                                        <SmallButton
                                            className="copy"
                                            onClick={() => copyToClipboard(mapping.encrypted_qr)}
                                        >
                                            📋 העתק QR
                                        </SmallButton>
                                        <SmallButton
                                            className="delete"
                                            onClick={() => handleDelete(mapping.id)}
                                        >
                                            🗑️ מחק
                                        </SmallButton>
                                    </ActionButtons>
                                </MappingCard>
                            ))}
                        </Grid>
                    )}
                </Card>
            </Container>
        </Layout>
    );
}
