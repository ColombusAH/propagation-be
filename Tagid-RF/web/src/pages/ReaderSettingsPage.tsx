import { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { theme } from '@/styles/theme';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface ReaderStatus {
    is_connected: boolean;
    is_scanning: boolean;
    reader_ip: string;
    reader_port: number;
}

interface NetworkConfig {
    ip: string;
    subnet: string;
    gateway: string;
    port: number;
    error?: string;
}

// Professional color palette (consistent with Dashboard)
const colors = {
    primary: '#1e40af',
    success: '#059669',
    danger: '#dc2626',
    dark: '#1e293b',
    slate: '#475569',
};

// Styled Components
const Container = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background: #f8fafc;
  min-height: 100vh;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 1.75rem;
  font-weight: 700;
  color: ${colors.dark};
`;

const StatusBadge = styled.span<{ active: boolean }>`
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  background: ${props => props.active ? colors.success : colors.danger};
  color: white;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
`;

const CardTitle = styled.h2`
  font-size: 1rem;
  font-weight: 600;
  color: ${colors.dark};
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
`;

const FormGroup = styled.div`
  margin-bottom: 1rem;
`;

const Label = styled.label`
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: ${theme.colors.textSecondary};
  margin-bottom: 0.5rem;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid ${theme.colors.border};
  border-radius: 10px;
  font-size: 1rem;
  background: ${theme.colors.background};
  color: ${theme.colors.text};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid ${theme.colors.border};
  border-radius: 10px;
  font-size: 1rem;
  background: ${theme.colors.background};
  color: ${theme.colors.text};
`;

const Button = styled.button<{ variant?: 'primary' | 'danger' | 'success' }>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  
  background: ${props => {
        switch (props.variant) {
            case 'danger': return colors.danger;
            case 'success': return colors.success;
            default: return colors.primary;
        }
    }};
  color: white;
  
  &:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
`;

const Slider = styled.input`
  width: 100%;
  margin: 0.5rem 0;
`;

const SliderValue = styled.span`
  font-size: 1.2rem;
  font-weight: 700;
  color: ${theme.colors.primary};
`;

const Message = styled.div<{ type: 'success' | 'error' }>`
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  background: ${props => props.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)'};
  color: ${props => props.type === 'success' ? '#10b981' : '#ef4444'};
  border: 1px solid currentColor;
`;

const RelayButton = styled.button<{ active: boolean }>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.active ? 'linear-gradient(135deg, #10b981, #059669)' : 'linear-gradient(135deg, #6b7280, #4b5563)'};
  color: white;
  
  &:hover {
    transform: scale(1.05);
  }
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid ${theme.colors.border};
  
  &:last-child {
    border-bottom: none;
  }
`;

const InfoLabel = styled.span`
  color: ${theme.colors.textSecondary};
`;

const InfoValue = styled.span`
  font-weight: 600;
  color: ${theme.colors.text};
`;

const MaterialIcon = ({ name, size = 20 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

export default function ReaderSettingsPage() {
    const { token } = useAuth();
    const [status, setStatus] = useState<ReaderStatus | null>(null);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [loading, setLoading] = useState(false);

    // Power settings
    const [power, setPower] = useState(26);

    // Relay states
    const [relay1, setRelay1] = useState(false);
    const [relay2, setRelay2] = useState(false);

    // Network settings
    const [networkConfig, setNetworkConfig] = useState<NetworkConfig>({
        ip: '192.168.1.200',
        subnet: '255.255.255.0',
        gateway: '192.168.1.1',
        port: 4001,
    });

    // RSSI filter
    const [rssiAntenna, setRssiAntenna] = useState(1);
    const [rssiThreshold, setRssiThreshold] = useState(50);

    // Gate settings
    const [gateEnabled, setGateEnabled] = useState(true);
    const [gateSensitivity, setGateSensitivity] = useState(80);

    const authHeaders = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };

    useEffect(() => {
        fetchStatus();
    }, []);

    const fetchStatus = async () => {
        try {
            const response = await fetch('/api/v1/rfid-scan/status');
            if (response.ok) {
                const data = await response.json();
                setStatus(data);
            }
        } catch (error) {
            console.error('Failed to fetch status:', error);
        }
    };

    const showMessage = (type: 'success' | 'error', text: string) => {
        setMessage({ type, text });
        setTimeout(() => setMessage(null), 3000);
    };

    const handleConnect = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/rfid-scan/connect', {
                method: 'POST',
                headers: authHeaders,
            });
            if (response.ok) {
                showMessage('success', '✅ התחבר בהצלחה לקורא');
                fetchStatus();
            } else {
                const err = await response.json();
                showMessage('error', err.detail || 'שגיאה בחיבור');
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
        setLoading(false);
    };

    const handleDisconnect = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/rfid-scan/disconnect', {
                method: 'POST',
                headers: authHeaders,
            });
            if (response.ok) {
                showMessage('success', '🔌 התנתק מהקורא');
                fetchStatus();
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
        setLoading(false);
    };

    const handleSetPower = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/rfid-scan/power', {
                method: 'POST',
                headers: authHeaders,
                body: JSON.stringify({ power_dbm: power }),
            });
            if (response.ok) {
                showMessage('success', `⚡ עוצמה הוגדרה ל-${power} dBm`);
            } else {
                const err = await response.json();
                showMessage('error', err.detail || 'שגיאה');
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
        setLoading(false);
    };

    const handleRelay = async (relayNum: number, close: boolean) => {
        try {
            const response = await fetch(`/api/v1/rfid-scan/relay/${relayNum}`, {
                method: 'POST',
                headers: authHeaders,
                body: JSON.stringify({ close }),
            });
            if (response.ok) {
                if (relayNum === 1) setRelay1(close);
                else setRelay2(close);
                showMessage('success', `🔔 ממסר ${relayNum} ${close ? 'הופעל' : 'כובה'}`);
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
    };

    const handleSetNetwork = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/rfid-scan/network', {
                method: 'POST',
                headers: authHeaders,
                body: JSON.stringify(networkConfig),
            });
            if (response.ok) {
                showMessage('success', '🌐 הגדרות רשת נשמרו. יש לאתחל את הקורא.');
            } else {
                const err = await response.json();
                showMessage('error', err.detail || 'שגיאה');
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
        setLoading(false);
    };

    const handleSetRssi = async () => {
        try {
            const response = await fetch('/api/v1/rfid-scan/rssi-filter', {
                method: 'POST',
                headers: authHeaders,
                body: JSON.stringify({ antenna: rssiAntenna, threshold: rssiThreshold }),
            });
            if (response.ok) {
                showMessage('success', `📶 סף RSSI הוגדר ל-${rssiThreshold}`);
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
    };

    const handleSetGate = async () => {
        try {
            const response = await fetch('/api/v1/rfid-scan/gate/config', {
                method: 'POST',
                headers: authHeaders,
                body: JSON.stringify({
                    mode: gateEnabled ? 1 : 0,
                    sensitivity: gateSensitivity,
                    direction_detect: true,
                }),
            });
            if (response.ok) {
                showMessage('success', '🚪 הגדרות שער נשמרו');
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
    };

    const handleInitialize = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/rfid-scan/initialize', {
                method: 'POST',
                headers: authHeaders,
            });
            if (response.ok) {
                showMessage('success', '🔄 הקורא אותחל בהצלחה');
            } else {
                const err = await response.json();
                showMessage('error', err.detail || 'שגיאה');
            }
        } catch (error) {
            showMessage('error', 'שגיאת רשת');
        }
        setLoading(false);
    };

    return (
        <Layout>
            <Container>
                <Header>
                    <Title style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <MaterialIcon name="settings" size={28} />
                        הגדרות קורא RFID
                    </Title>
                    <StatusBadge active={status?.is_connected ?? false}>
                        <MaterialIcon name={status?.is_connected ? 'check_circle' : 'cancel'} size={16} />
                        {' '}{status?.is_connected ? 'מחובר' : 'מנותק'}
                    </StatusBadge>
                </Header>

                {message && (
                    <Message type={message.type}>{message.text}</Message>
                )}

                <Grid>
                    {/* Connection Card */}
                    <Card>
                        <CardTitle><MaterialIcon name="power" size={20} /> חיבור</CardTitle>
                        {status && (
                            <>
                                <InfoRow>
                                    <InfoLabel>כתובת IP</InfoLabel>
                                    <InfoValue>{status.reader_ip}</InfoValue>
                                </InfoRow>
                                <InfoRow>
                                    <InfoLabel>פורט</InfoLabel>
                                    <InfoValue>{status.reader_port}</InfoValue>
                                </InfoRow>
                                <InfoRow>
                                    <InfoLabel>סריקה</InfoLabel>
                                    <InfoValue style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <MaterialIcon name={status.is_scanning ? 'sync' : 'pause'} size={16} />
                                        {status.is_scanning ? 'פעיל' : 'מושהה'}
                                    </InfoValue>
                                </InfoRow>
                            </>
                        )}
                        <ButtonGroup style={{ marginTop: '1rem' }}>
                            <Button onClick={handleConnect} disabled={loading || status?.is_connected}>
                                <MaterialIcon name="link" size={18} /> התחבר
                            </Button>
                            <Button variant="danger" onClick={handleDisconnect} disabled={loading || !status?.is_connected}>
                                <MaterialIcon name="link_off" size={18} /> התנתק
                            </Button>
                            <Button onClick={handleInitialize} disabled={loading}>
                                <MaterialIcon name="refresh" size={18} /> אתחל
                            </Button>
                        </ButtonGroup>
                    </Card>

                    {/* Power Card */}
                    <Card>
                        <CardTitle><MaterialIcon name="bolt" size={20} /> עוצמת שידור RF</CardTitle>
                        <FormGroup>
                            <Label>עוצמה (dBm): <SliderValue>{power}</SliderValue></Label>
                            <Slider
                                type="range"
                                min="0"
                                max="30"
                                value={power}
                                onChange={(e) => setPower(Number(e.target.value))}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: theme.colors.textSecondary }}>
                                <span>0 (חלש)</span>
                                <span>30 (חזק)</span>
                            </div>
                        </FormGroup>
                        <Button onClick={handleSetPower} disabled={loading}>
                            <MaterialIcon name="save" size={18} /> שמור עוצמה
                        </Button>
                    </Card>

                    {/* Buzzer/Relay Card */}
                    <Card>
                        <CardTitle><MaterialIcon name="notifications" size={20} /> זמזם / ממסרים</CardTitle>
                        <p style={{ fontSize: '0.85rem', color: theme.colors.textSecondary, marginBottom: '1rem' }}>
                            הפעל ממסרים לשליטה בזמזם או התקנים חיצוניים
                        </p>
                        <ButtonGroup>
                            <RelayButton
                                active={relay1}
                                onClick={() => handleRelay(1, !relay1)}
                            >
                                <MaterialIcon name={relay1 ? 'toggle_on' : 'toggle_off'} size={20} /> ממסר 1
                            </RelayButton>
                            <RelayButton
                                active={relay2}
                                onClick={() => handleRelay(2, !relay2)}
                            >
                                <MaterialIcon name={relay2 ? 'toggle_on' : 'toggle_off'} size={20} /> ממסר 2
                            </RelayButton>
                        </ButtonGroup>
                    </Card>

                    {/* RSSI Filter Card */}
                    <Card>
                        <CardTitle><MaterialIcon name="signal_cellular_alt" size={20} /> סינון RSSI</CardTitle>
                        <FormGroup>
                            <Label>אנטנה</Label>
                            <Select value={rssiAntenna} onChange={(e) => setRssiAntenna(Number(e.target.value))}>
                                <option value={1}>אנטנה 1</option>
                                <option value={2}>אנטנה 2</option>
                                <option value={3}>אנטנה 3</option>
                                <option value={4}>אנטנה 4</option>
                            </Select>
                        </FormGroup>
                        <FormGroup>
                            <Label>סף RSSI: <SliderValue>{rssiThreshold}</SliderValue></Label>
                            <Slider
                                type="range"
                                min="0"
                                max="100"
                                value={rssiThreshold}
                                onChange={(e) => setRssiThreshold(Number(e.target.value))}
                            />
                        </FormGroup>
                        <Button onClick={handleSetRssi}>
                            <MaterialIcon name="save" size={18} /> שמור
                        </Button>
                    </Card>

                    {/* Network Card */}
                    <Card>
                        <CardTitle><MaterialIcon name="language" size={20} /> הגדרות רשת</CardTitle>
                        <FormGroup>
                            <Label>כתובת IP</Label>
                            <Input
                                value={networkConfig.ip}
                                onChange={(e) => setNetworkConfig({ ...networkConfig, ip: e.target.value })}
                                placeholder="192.168.1.200"
                            />
                        </FormGroup>
                        <FormGroup>
                            <Label>Subnet Mask</Label>
                            <Input
                                value={networkConfig.subnet}
                                onChange={(e) => setNetworkConfig({ ...networkConfig, subnet: e.target.value })}
                                placeholder="255.255.255.0"
                            />
                        </FormGroup>
                        <FormGroup>
                            <Label>Gateway</Label>
                            <Input
                                value={networkConfig.gateway}
                                onChange={(e) => setNetworkConfig({ ...networkConfig, gateway: e.target.value })}
                                placeholder="192.168.1.1"
                            />
                        </FormGroup>
                        <FormGroup>
                            <Label>Port</Label>
                            <Input
                                type="number"
                                value={networkConfig.port}
                                onChange={(e) => setNetworkConfig({ ...networkConfig, port: Number(e.target.value) })}
                            />
                        </FormGroup>
                        <Button onClick={handleSetNetwork} disabled={loading}>
                            <MaterialIcon name="save" size={18} /> שמור הגדרות
                        </Button>
                    </Card>

                    {/* Gate Card */}
                    <Card>
                        <CardTitle><MaterialIcon name="meeting_room" size={20} /> מצב שער</CardTitle>
                        <FormGroup>
                            <Label>
                                <input
                                    type="checkbox"
                                    checked={gateEnabled}
                                    onChange={(e) => setGateEnabled(e.target.checked)}
                                    style={{ marginLeft: '0.5rem' }}
                                />
                                הפעל זיהוי מעבר
                            </Label>
                        </FormGroup>
                        <FormGroup>
                            <Label>רגישות: <SliderValue>{gateSensitivity}</SliderValue></Label>
                            <Slider
                                type="range"
                                min="0"
                                max="255"
                                value={gateSensitivity}
                                onChange={(e) => setGateSensitivity(Number(e.target.value))}
                            />
                        </FormGroup>
                        <Button onClick={handleSetGate}>
                            <MaterialIcon name="save" size={18} /> שמור
                        </Button>
                    </Card>
                </Grid>
            </Container>
        </Layout>
    );
}
