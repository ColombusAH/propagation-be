import { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const pulse = keyframes`
  0% { box-shadow: 0 0 0 0 ${theme.colors.error}B3; }
  70% { box-shadow: 0 0 0 20px ${theme.colors.error}00; }
  100% { box-shadow: 0 0 0 0 ${theme.colors.error}00; }
`;

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, ${theme.colors.gray[50]} 0%, ${theme.colors.gray[100]} 100%);
  min-height: calc(100vh - 64px);
  animation: ${theme.animations.fadeIn};
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
  background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryDark} 100%);
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.lg};
  border-right: 10px solid ${theme.colors.primaryDark};
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: ${theme.animations.slideUp};

  h1, p {
    color: white;
  }
`;

const HeaderContent = styled.div``;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  margin: 0;
  line-height: 1.2;
`;

const Subtitle = styled.p`
  margin: ${theme.spacing.sm} 0 0 0;
  opacity: 0.9;
`;

const StatusBadge = styled.div < { $active?: boolean } > `
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  background: ${props => props.$active ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'};
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.full};
  font-weight: ${theme.typography.fontWeight.bold};

  .material-symbols-outlined {
    font-size: 24px;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.xl};

  @media (max-width: 1000px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  box-shadow: ${theme.shadows.md};
  animation: ${theme.animations.slideUp};
`;

const CardTitle = styled.h2`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.md} 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};

  .material-symbols-outlined {
    font-size: 28px;
    color: ${theme.colors.error};
  }
`;

const AlertCard = styled.div < { $active?: boolean } > `
  background: ${props => props.$active ? theme.colors.errorLight : 'white'};
  border: 2px solid ${props => props.$active ? theme.colors.error : theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  margin-bottom: ${theme.spacing.lg};
  animation: ${props => props.$active ? pulse : 'none'};
  transition: all ${theme.transitions.base};
`;

const AlertHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${theme.spacing.md};
`;

const AlertTitle = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.errorDark};

  .material-symbols-outlined {
    font-size: 28px;
  }
`;

const AlertTime = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textMuted};
`;

const AlertDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const AlertRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: ${theme.spacing.sm} 0;
  border-bottom: 1px solid ${theme.colors.borderLight};

  &:last-child {
    border-bottom: none;
  }
`;

const AlertLabel = styled.span`
  color: ${theme.colors.textSecondary};
`;

const AlertValue = styled.span`
  font-weight: ${theme.typography.fontWeight.semibold};
  font-family: monospace;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.lg};
`;

const DismissButton = styled.button`
  flex: 1;
  padding: ${theme.spacing.md};
  background: ${theme.colors.gray[100]};
  color: ${theme.colors.text};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.gray[200]};
  }
`;

const ResolveButton = styled.button`
  flex: 1;
  padding: ${theme.spacing.md};
  background: linear-gradient(135deg, ${theme.colors.success} 0%, ${theme.colors.successDark} 100%);
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};
  transition: all ${theme.transitions.fast};

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${theme.shadows.md};
  }

  .material-symbols-outlined {
    font-size: 20px;
  }
`;

const ScansList = styled.div`
  max-height: 400px;
  overflow-y: auto;
`;

const ScanItem = styled.div < { $paid?: boolean } > `
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${theme.spacing.md};
  border: 1px solid ${props => props.$paid ? theme.colors.success : theme.colors.error};
  border-radius: ${theme.borderRadius.lg};
  margin-bottom: ${theme.spacing.sm};
  background: ${props => props.$paid ? `${theme.colors.success}05` : `${theme.colors.error}05`};
`;

const ScanInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ScanEpc = styled.span`
  font-family: monospace;
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text};
  font-weight: ${theme.typography.fontWeight.semibold};
`;

const ScanMeta = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textMuted};
`;

const ScanStatus = styled.span < { $paid?: boolean } > `
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.bold};
  background: ${props => props.$paid ? theme.colors.successLight : theme.colors.errorLight};
  color: ${props => props.$paid ? theme.colors.successDark : theme.colors.errorDark};
`;

const SimulateButton = styled.button`
  width: 100%;
  padding: ${theme.spacing.lg};
  background: linear-gradient(135deg, ${theme.colors.error} 0%, ${theme.colors.errorDark} 100%);
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  transition: all ${theme.transitions.base};
  box-shadow: ${theme.shadows.lg};
  margin-bottom: ${theme.spacing.lg};

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px ${theme.colors.error}40;
  }

  .material-symbols-outlined {
    font-size: 24px;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing['3xl']};
  color: ${theme.colors.textMuted};

  .material-symbols-outlined {
    font-size: 64px;
    color: ${theme.colors.primary}40;
    margin-bottom: ${theme.spacing.md};
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
`;

const StatCard = styled.div < { $color: string } > `
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  text-align: center;
  border-top: 4px solid ${props => props.$color};
`;

const StatValue = styled.div < { $color: string } > `
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${props => props.$color};
`;

const StatLabel = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textMuted};
  margin-top: ${theme.spacing.xs};
`;

interface GateScan {
    id: string;
    epc: string;
    productName?: string;
    isPaid: boolean;
    scannedAt: Date;
}

interface TheftAlert {
    id: string;
    epc: string;
    productName: string;
    productPrice: number;
    detectedAt: Date;
    isActive: boolean;
}

export function ExitGatePage() {
    const { userRole } = useAuth();
    const [isMonitoring] = useState(true);
    const [scans, setScans] = useState < GateScan[] > ([]);
    const [alerts, setAlerts] = useState < TheftAlert[] > ([]);

    const isManager = userRole && ['SUPER_ADMIN', 'NETWORK_ADMIN', 'STORE_MANAGER'].includes(userRole);

    if (!isManager) {
        return (
            <Layout>
                <Container>
                    <Card>
                        <CardTitle>אין גישה</CardTitle>
                        <p>עמוד זה זמין רק למנהלים</p>
                    </Card>
                </Container>
            </Layout>
        );
    }

    const simulateUnpaidExit = () => {
        const products = [
            { name: 'חולצת טי כחולה', price: 89.90 },
            { name: 'מכנסי ג\'ינס', price: 199.90 },
            { name: 'נעלי ספורט', price: 349.90 },
        ];

        const randomProduct = products[Math.floor(Math.random() * products.length)];
        const newEpc = `E2${Math.random().toString(16).substring(2, 18).toUpperCase()}`;

        const newScan: GateScan = {
            id: crypto.randomUUID(),
            epc: newEpc,
            productName: randomProduct.name,
            isPaid: false,
            scannedAt: new Date(),
        };

        const newAlert: TheftAlert = {
            id: crypto.randomUUID(),
            epc: newEpc,
            productName: randomProduct.name,
            productPrice: randomProduct.price,
            detectedAt: new Date(),
            isActive: true,
        };

        setScans(prev => [newScan, ...prev]);
        setAlerts(prev => [newAlert, ...prev]);

        if (Notification.permission === 'granted') {
            new Notification('התראת אבטחה!', {
                body: `מוצר לא שולם יצא מהחנות: ${randomProduct.name}`,
                icon: '/favicon.ico',
                tag: 'theft-alert',
            });
        }
    };

    const simulatePaidExit = () => {
        const products = [
            { name: 'שעון יד', price: 299.90 },
            { name: 'תיק גב', price: 149.90 },
        ];

        const randomProduct = products[Math.floor(Math.random() * products.length)];
        const newEpc = `E2${Math.random().toString(16).substring(2, 18).toUpperCase()}`;

        const newScan: GateScan = {
            id: crypto.randomUUID(),
            epc: newEpc,
            productName: randomProduct.name,
            isPaid: true,
            scannedAt: new Date(),
        };

        setScans(prev => [newScan, ...prev]);
    };

    const resolveAlert = (id: string) => {
        setAlerts(prev => prev.map(a =>
            a.id === id ? { ...a, isActive: false } : a
        ));
    };

    const dismissAlert = (id: string) => {
        setAlerts(prev => prev.filter(a => a.id !== id));
    };

    const activeAlerts = alerts.filter(a => a.isActive);
    const totalScans = scans.length;
    const paidScans = scans.filter(s => s.isPaid).length;
    const unpaidScans = scans.filter(s => !s.isPaid).length;

    return (
        <Layout>
            <Container>
                <Header>
                    <HeaderContent>
                        <Title>מעקב שער יציאה</Title>
                        <Subtitle>ניטור תגים בשער וזיהוי פריטים לא שולמו</Subtitle>
                    </HeaderContent>
                    <StatusBadge $active={isMonitoring}>
                        <span className="material-symbols-outlined">
                            {isMonitoring ? 'sensors' : 'sensors_off'}
                        </span>
                        {isMonitoring ? 'פעיל' : 'לא פעיל'}
                    </StatusBadge>
                </Header>

                <StatsGrid>
                    <StatCard $color={theme.colors.primary}>
                        <StatValue $color={theme.colors.primary}>{totalScans}</StatValue>
                        <StatLabel>סה"כ סריקות</StatLabel>
                    </StatCard>
                    <StatCard $color={theme.colors.success}>
                        <StatValue $color={theme.colors.success}>{paidScans}</StatValue>
                        <StatLabel>שולמו</StatLabel>
                    </StatCard>
                    <StatCard $color={theme.colors.error}>
                        <StatValue $color={theme.colors.error}>{unpaidScans}</StatValue>
                        <StatLabel>לא שולמו</StatLabel>
                    </StatCard>
                </StatsGrid>

                <Grid>
                    <Card>
                        <CardTitle>
                            <span className="material-symbols-outlined">warning</span>
                            התראות פעילות ({activeAlerts.length})
                        </CardTitle>

                        <SimulateButton onClick={simulateUnpaidExit}>
                            <span className="material-symbols-outlined">directions_run</span>
                            סמלץ יציאה ללא תשלום
                        </SimulateButton>

                        {activeAlerts.length === 0 ? (
                            <EmptyState>
                                <span className="material-symbols-outlined">verified_user</span>
                                <p>אין התראות פעילות</p>
                                <p style={{ fontSize: theme.typography.fontSize.sm }}>המערכת מנטרת את שער היציאה</p>
                            </EmptyState>
                        ) : (
                            activeAlerts.map(alert => (
                                <AlertCard key={alert.id} $active={alert.isActive}>
                                    <AlertHeader>
                                        <AlertTitle>
                                            <span className="material-symbols-outlined">error</span>
                                            פריט לא שולם!
                                        </AlertTitle>
                                        <AlertTime>{alert.detectedAt.toLocaleTimeString('he-IL')}</AlertTime>
                                    </AlertHeader>
                                    <AlertDetails>
                                        <AlertRow>
                                            <AlertLabel>מוצר:</AlertLabel>
                                            <AlertValue>{alert.productName}</AlertValue>
                                        </AlertRow>
                                        <AlertRow>
                                            <AlertLabel>מחיר:</AlertLabel>
                                            <AlertValue>{alert.productPrice.toFixed(2)} ש"ח</AlertValue>
                                        </AlertRow>
                                        <AlertRow>
                                            <AlertLabel>EPC:</AlertLabel>
                                            <AlertValue>{alert.epc}</AlertValue>
                                        </AlertRow>
                                    </AlertDetails>
                                    <ActionButtons>
                                        <DismissButton onClick={() => dismissAlert(alert.id)}>
                                            בטל התראה
                                        </DismissButton>
                                        <ResolveButton onClick={() => resolveAlert(alert.id)}>
                                            <span className="material-symbols-outlined">check</span>
                                            טופל
                                        </ResolveButton>
                                    </ActionButtons>
                                </AlertCard>
                            ))
                        )}
                    </Card>

                    <Card>
                        <CardTitle>
                            <span className="material-symbols-outlined">history</span>
                            היסטוריית סריקות
                        </CardTitle>

                        <SimulateButton
                            onClick={simulatePaidExit}
                            style={{ background: `linear-gradient(135deg, ${theme.colors.success} 0%, ${theme.colors.successDark} 100%)` }}
                        >
                            <span className="material-symbols-outlined">check_circle</span>
                            סמלץ יציאה עם תשלום
                        </SimulateButton>

                        <ScansList>
                            {scans.length === 0 ? (
                                <EmptyState>
                                    <span className="material-symbols-outlined">sensors</span>
                                    <p>אין סריקות עדיין</p>
                                    <p style={{ fontSize: theme.typography.fontSize.sm }}>סריקות משער היציאה יופיעו כאן</p>
                                </EmptyState>
                            ) : (
                                scans.map(scan => (
                                    <ScanItem key={scan.id} $paid={scan.isPaid}>
                                        <ScanInfo>
                                            <ScanEpc>{scan.productName || scan.epc}</ScanEpc>
                                            <ScanMeta>{scan.scannedAt.toLocaleTimeString('he-IL')}</ScanMeta>
                                        </ScanInfo>
                                        <ScanStatus $paid={scan.isPaid}>
                                            {scan.isPaid ? 'שולם' : 'לא שולם'}
                                        </ScanStatus>
                                    </ScanItem>
                                ))
                            )}
                        </ScansList>
                    </Card>
                </Grid>
            </Container>
        </Layout>
    );
}
