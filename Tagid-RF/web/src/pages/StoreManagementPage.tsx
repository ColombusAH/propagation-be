import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.xl};
  flex-wrap: wrap;
  gap: ${theme.spacing.md};
`;

const HeaderLeft = styled.div``;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.xs} 0;
`;

const Subtitle = styled.p`
  color: ${theme.colors.textSecondary};
  margin: 0;
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' | 'danger' }>`
  background-color: ${props => {
        switch (props.$variant) {
            case 'secondary': return theme.colors.backgroundAlt;
            case 'danger': return theme.colors.error;
            default: return theme.colors.primary;
        }
    }};
  color: ${props => props.$variant === 'secondary' ? theme.colors.text : 'white'};
  border: 1px solid ${props => {
        switch (props.$variant) {
            case 'secondary': return theme.colors.border;
            case 'danger': return theme.colors.error;
            default: return theme.colors.primary;
        }
    }};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.base};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StoresGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: ${theme.spacing.lg};
`;

const StoreCard = styled.div`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  transition: all ${theme.transitions.fast};

  &:hover {
    box-shadow: ${theme.shadows.md};
  }
`;

const StoreHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: ${theme.spacing.md};
`;

const StoreName = styled.h3`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
`;

const StoreStatus = styled.span<{ $active: boolean }>`
  background: ${props => props.$active ? theme.colors.success : '#9CA3AF'};
  color: white;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const StoreDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
  margin-bottom: ${theme.spacing.md};
`;

const DetailRow = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  font-size: ${theme.typography.fontSize.sm};
`;

const DetailLabel = styled.span`
  color: ${theme.colors.textSecondary};
  min-width: 80px;
`;

const DetailValue = styled.span`
  color: ${theme.colors.text};
`;

const StoreStats = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: ${theme.spacing.sm};
  padding: ${theme.spacing.md};
  background: ${theme.colors.backgroundAlt};
  border-radius: ${theme.borderRadius.md};
  margin-bottom: ${theme.spacing.md};
`;

const Stat = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
`;

const StatLabel = styled.div`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textSecondary};
`;

const StoreActions = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: ${theme.colors.surface};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.xl};
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
`;

const ModalTitle = styled.h2`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.semibold};
  margin: 0 0 ${theme.spacing.lg} 0;
`;

const FormGroup = styled.div`
  margin-bottom: ${theme.spacing.md};
`;

const Label = styled.label`
  display: block;
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.xs};
`;

const Input = styled.input`
  width: 100%;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Select = styled.select`
  width: 100%;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: white;

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const ModalActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.lg};
`;

const AccessDenied = styled.div`
  text-align: center;
  padding: ${theme.spacing['2xl']};
`;

interface Store {
    id: string;
    name: string;
    address: string;
    phone: string;
    manager: string | null;
    managerName: string | null;
    isActive: boolean;
    stats: {
        sellers: number;
        todaySales: number;
        monthlyRevenue: number;
    };
}

// Mock data
const mockStores: Store[] = [
    {
        id: '1',
        name: 'סניף תל אביב',
        address: 'דיזנגוף 100, תל אביב',
        phone: '03-1234567',
        manager: 'user-1',
        managerName: 'דני לוי',
        isActive: true,
        stats: { sellers: 5, todaySales: 48, monthlyRevenue: 125000 },
    },
    {
        id: '2',
        name: 'סניף ירושלים',
        address: 'יפו 50, ירושלים',
        phone: '02-7654321',
        manager: 'user-2',
        managerName: 'שרה כהן',
        isActive: true,
        stats: { sellers: 3, todaySales: 32, monthlyRevenue: 89000 },
    },
    {
        id: '3',
        name: 'סניף חיפה',
        address: 'הנמל 25, חיפה',
        phone: '04-9876543',
        manager: null,
        managerName: null,
        isActive: false,
        stats: { sellers: 0, todaySales: 0, monthlyRevenue: 0 },
    },
];

const mockManagers = [
    { id: 'user-1', name: 'דני לוי' },
    { id: 'user-2', name: 'שרה כהן' },
    { id: 'user-3', name: 'יוסי אברהם' },
    { id: 'user-4', name: 'רונית מזרחי' },
];

/**
 * StoreManagementPage - Manage stores for chain admin
 * Create new stores, assign managers, view statistics
 */
export function StoreManagementPage() {
    const { userRole } = useAuth();
    const [stores, setStores] = useState<Store[]>(mockStores);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showAssignModal, setShowAssignModal] = useState<string | null>(null);
    const [newStore, setNewStore] = useState({ name: '', address: '', phone: '' });
    const [selectedManager, setSelectedManager] = useState('');

    const isChainAdmin = userRole === 'ADMIN';

    if (!isChainAdmin) {
        return (
            <Layout>
                <Container>
                    <AccessDenied>
                        <Title>אין גישה</Title>
                        <Subtitle>עמוד זה זמין רק למנהל רשת</Subtitle>
                    </AccessDenied>
                </Container>
            </Layout>
        );
    }

    const handleCreateStore = () => {
        if (!newStore.name || !newStore.address) return;

        const store: Store = {
            id: Date.now().toString(),
            name: newStore.name,
            address: newStore.address,
            phone: newStore.phone,
            manager: null,
            managerName: null,
            isActive: true,
            stats: { sellers: 0, todaySales: 0, monthlyRevenue: 0 },
        };

        setStores([...stores, store]);
        setNewStore({ name: '', address: '', phone: '' });
        setShowCreateModal(false);
        alert('חנות נוצרה בהצלחה!');
    };

    const handleAssignManager = () => {
        if (!showAssignModal || !selectedManager) return;

        const manager = mockManagers.find(m => m.id === selectedManager);
        setStores(stores.map(store => {
            if (store.id === showAssignModal) {
                return { ...store, manager: selectedManager, managerName: manager?.name || null };
            }
            return store;
        }));

        setShowAssignModal(null);
        setSelectedManager('');
        alert('מנהל שויך בהצלחה!');
    };

    const toggleStoreStatus = (storeId: string) => {
        setStores(stores.map(store => {
            if (store.id === storeId) {
                return { ...store, isActive: !store.isActive };
            }
            return store;
        }));
    };

    return (
        <Layout>
            <Container>
                <Header>
                    <HeaderLeft>
                        <Title>ניהול חנויות</Title>
                        <Subtitle>צור חנויות חדשות ושייך מנהלים</Subtitle>
                    </HeaderLeft>
                    <Button onClick={() => setShowCreateModal(true)}>
                        + חנות חדשה
                    </Button>
                </Header>

                <StoresGrid>
                    {stores.map(store => (
                        <StoreCard key={store.id}>
                            <StoreHeader>
                                <StoreName>{store.name}</StoreName>
                                <StoreStatus $active={store.isActive}>
                                    {store.isActive ? 'פעיל' : 'לא פעיל'}
                                </StoreStatus>
                            </StoreHeader>

                            <StoreDetails>
                                <DetailRow>
                                    <DetailLabel>כתובת:</DetailLabel>
                                    <DetailValue>{store.address}</DetailValue>
                                </DetailRow>
                                <DetailRow>
                                    <DetailLabel>טלפון:</DetailLabel>
                                    <DetailValue>{store.phone || 'לא הוגדר'}</DetailValue>
                                </DetailRow>
                                <DetailRow>
                                    <DetailLabel>מנהל:</DetailLabel>
                                    <DetailValue>
                                        {store.managerName || (
                                            <span style={{ color: theme.colors.error }}>לא שויך</span>
                                        )}
                                    </DetailValue>
                                </DetailRow>
                            </StoreDetails>

                            <StoreStats>
                                <Stat>
                                    <StatValue>{store.stats.sellers}</StatValue>
                                    <StatLabel>מוכרים</StatLabel>
                                </Stat>
                                <Stat>
                                    <StatValue>{store.stats.todaySales}</StatValue>
                                    <StatLabel>מכירות היום</StatLabel>
                                </Stat>
                                <Stat>
                                    <StatValue>₪{(store.stats.monthlyRevenue / 1000).toFixed(0)}K</StatValue>
                                    <StatLabel>הכנסות חודשי</StatLabel>
                                </Stat>
                            </StoreStats>

                            <StoreActions>
                                <Button $variant="secondary" onClick={() => setShowAssignModal(store.id)}>
                                    {store.manager ? 'החלף מנהל' : 'שייך מנהל'}
                                </Button>
                                <Button
                                    $variant={store.isActive ? 'danger' : 'primary'}
                                    onClick={() => toggleStoreStatus(store.id)}
                                >
                                    {store.isActive ? 'השבת' : 'הפעל'}
                                </Button>
                            </StoreActions>
                        </StoreCard>
                    ))}
                </StoresGrid>

                {/* Create Store Modal */}
                {showCreateModal && (
                    <Modal onClick={() => setShowCreateModal(false)}>
                        <ModalContent onClick={e => e.stopPropagation()}>
                            <ModalTitle>יצירת חנות חדשה</ModalTitle>

                            <FormGroup>
                                <Label>שם החנות *</Label>
                                <Input
                                    type="text"
                                    value={newStore.name}
                                    onChange={e => setNewStore({ ...newStore, name: e.target.value })}
                                    placeholder="סניף רמת גן"
                                />
                            </FormGroup>

                            <FormGroup>
                                <Label>כתובת *</Label>
                                <Input
                                    type="text"
                                    value={newStore.address}
                                    onChange={e => setNewStore({ ...newStore, address: e.target.value })}
                                    placeholder="ביאליק 50, רמת גן"
                                />
                            </FormGroup>

                            <FormGroup>
                                <Label>טלפון</Label>
                                <Input
                                    type="tel"
                                    value={newStore.phone}
                                    onChange={e => setNewStore({ ...newStore, phone: e.target.value })}
                                    placeholder="03-1234567"
                                />
                            </FormGroup>

                            <ModalActions>
                                <Button $variant="secondary" onClick={() => setShowCreateModal(false)}>
                                    ביטול
                                </Button>
                                <Button onClick={handleCreateStore} disabled={!newStore.name || !newStore.address}>
                                    צור חנות
                                </Button>
                            </ModalActions>
                        </ModalContent>
                    </Modal>
                )}

                {/* Assign Manager Modal */}
                {showAssignModal && (
                    <Modal onClick={() => setShowAssignModal(null)}>
                        <ModalContent onClick={e => e.stopPropagation()}>
                            <ModalTitle>שיוך מנהל לחנות</ModalTitle>

                            <FormGroup>
                                <Label>בחר מנהל</Label>
                                <Select
                                    value={selectedManager}
                                    onChange={e => setSelectedManager(e.target.value)}
                                >
                                    <option value="">בחר מנהל...</option>
                                    {mockManagers.map(manager => (
                                        <option key={manager.id} value={manager.id}>
                                            {manager.name}
                                        </option>
                                    ))}
                                </Select>
                            </FormGroup>

                            <ModalActions>
                                <Button $variant="secondary" onClick={() => setShowAssignModal(null)}>
                                    ביטול
                                </Button>
                                <Button onClick={handleAssignManager} disabled={!selectedManager}>
                                    שייך מנהל
                                </Button>
                            </ModalActions>
                        </ModalContent>
                    </Modal>
                )}
            </Container>
        </Layout>
    );
}
