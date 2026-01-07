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

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Filters = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
  flex-wrap: wrap;
`;

const Select = styled.select`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: white;
  min-width: 150px;

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Table = styled.table`
  width: 100%;
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  border-collapse: collapse;
  overflow: hidden;
`;

const Th = styled.th`
  text-align: right;
  padding: ${theme.spacing.md};
  background: ${theme.colors.backgroundAlt};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.textSecondary};
  border-bottom: 1px solid ${theme.colors.border};
`;

const Td = styled.td`
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.border};
  vertical-align: middle;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${theme.colors.primaryLight};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: ${theme.typography.fontWeight.semibold};
  font-size: ${theme.typography.fontSize.sm};
`;

const UserDetails = styled.div``;

const UserName = styled.div`
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const UserEmail = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const RoleBadge = styled.span<{ $role: string }>`
  display: inline-block;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  background: ${props => {
        switch (props.$role) {
            case 'ADMIN': return theme.colors.primary;
            case 'MANAGER': return theme.colors.success;
            case 'SELLER': return '#F59E0B';
            default: return theme.colors.textSecondary;
        }
    }};
  color: white;
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const StatusBadge = styled.span<{ $active: boolean }>`
  display: inline-block;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  background: ${props => props.$active ? theme.colors.success : '#9CA3AF'};
  color: white;
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.xs};
`;

const Actions = styled.div`
  display: flex;
  gap: ${theme.spacing.xs};
`;

const ActionButton = styled.button`
  background: none;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.sm};
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.backgroundAlt};
  }
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

const FormSelect = styled.select`
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

interface User {
    id: string;
    name: string;
    email: string;
    phone: string;
    role: 'ADMIN' | 'MANAGER' | 'SELLER';
    storeId: string | null;
    storeName: string | null;
    isActive: boolean;
    createdAt: string;
}

// Mock data
const mockUsers: User[] = [
    {
        id: '1',
        name: 'דני לוי',
        email: 'dani@store.com',
        phone: '052-1234567',
        role: 'MANAGER',
        storeId: '1',
        storeName: 'סניף תל אביב',
        isActive: true,
        createdAt: '2024-01-15',
    },
    {
        id: '2',
        name: 'שרה כהן',
        email: 'sara@store.com',
        phone: '053-7654321',
        role: 'MANAGER',
        storeId: '2',
        storeName: 'סניף ירושלים',
        isActive: true,
        createdAt: '2024-02-20',
    },
    {
        id: '3',
        name: 'יוסי אברהם',
        email: 'yosi@store.com',
        phone: '054-1111111',
        role: 'SELLER',
        storeId: '1',
        storeName: 'סניף תל אביב',
        isActive: true,
        createdAt: '2024-03-10',
    },
    {
        id: '4',
        name: 'רונית מזרחי',
        email: 'ronit@store.com',
        phone: '054-2222222',
        role: 'SELLER',
        storeId: '1',
        storeName: 'סניף תל אביב',
        isActive: true,
        createdAt: '2024-03-15',
    },
    {
        id: '5',
        name: 'משה גולן',
        email: 'moshe@store.com',
        phone: '054-3333333',
        role: 'SELLER',
        storeId: '2',
        storeName: 'סניף ירושלים',
        isActive: false,
        createdAt: '2024-01-20',
    },
];

const mockStores = [
    { id: '1', name: 'סניף תל אביב' },
    { id: '2', name: 'סניף ירושלים' },
    { id: '3', name: 'סניף חיפה' },
];

const roleLabels: Record<string, string> = {
    ADMIN: 'מנהל רשת',
    MANAGER: 'מנהל חנות',
    SELLER: 'מוכר',
};

/**
 * UserManagementPage - Manage users and store assignments
 * - CHAIN_ADMIN: Can manage all users
 * - STORE_MANAGER: Can manage sellers in their store
 */
export function UserManagementPage() {
    const { userRole } = useAuth();
    const [users, setUsers] = useState<User[]>(mockUsers);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [filterRole, setFilterRole] = useState<string>('all');
    const [filterStore, setFilterStore] = useState<string>('all');
    const [newUser, setNewUser] = useState({
        name: '',
        email: '',
        phone: '',
        role: 'SELLER' as 'MANAGER' | 'SELLER',
        storeId: '',
    });

    const isChainAdmin = userRole === 'ADMIN';
    const isManager = userRole === 'MANAGER';
    const canManageUsers = isChainAdmin || isManager;

    if (!canManageUsers) {
        return (
            <Layout>
                <Container>
                    <AccessDenied>
                        <Title>אין גישה</Title>
                        <Subtitle>עמוד זה זמין רק למנהלים</Subtitle>
                    </AccessDenied>
                </Container>
            </Layout>
        );
    }

    // Filter users based on role and store
    const filteredUsers = users.filter(user => {
        // Store managers can only see sellers in their store
        if (isManager && !isChainAdmin) {
            if (user.role !== 'SELLER') return false;
            // In real app, filter by manager's store
        }

        if (filterRole !== 'all' && user.role !== filterRole) return false;
        if (filterStore !== 'all' && user.storeId !== filterStore) return false;
        return true;
    });

    const handleCreateUser = () => {
        if (!newUser.name || !newUser.email || !newUser.storeId) return;

        const store = mockStores.find(s => s.id === newUser.storeId);
        const user: User = {
            id: Date.now().toString(),
            name: newUser.name,
            email: newUser.email,
            phone: newUser.phone,
            role: newUser.role,
            storeId: newUser.storeId,
            storeName: store?.name || null,
            isActive: true,
            createdAt: new Date().toISOString().split('T')[0],
        };

        setUsers([...users, user]);
        setNewUser({ name: '', email: '', phone: '', role: 'SELLER', storeId: '' });
        setShowCreateModal(false);
        alert('משתמש נוצר בהצלחה!');
    };

    const toggleUserStatus = (userId: string) => {
        setUsers(users.map(user => {
            if (user.id === userId) {
                return { ...user, isActive: !user.isActive };
            }
            return user;
        }));
    };

    const getInitials = (name: string) => {
        return name.split(' ').map(n => n[0]).join('').slice(0, 2);
    };

    return (
        <Layout>
            <Container>
                <Header>
                    <HeaderLeft>
                        <Title>ניהול משתמשים</Title>
                        <Subtitle>
                            {isChainAdmin ? 'נהל מנהלים ומוכרים בכל החנויות' : 'נהל מוכרים בחנות שלך'}
                        </Subtitle>
                    </HeaderLeft>
                    <Button onClick={() => setShowCreateModal(true)}>
                        + משתמש חדש
                    </Button>
                </Header>

                <Filters>
                    {isChainAdmin && (
                        <Select value={filterRole} onChange={e => setFilterRole(e.target.value)}>
                            <option value="all">כל התפקידים</option>
                            <option value="MANAGER">מנהלי חנות</option>
                            <option value="SELLER">מוכרים</option>
                        </Select>
                    )}
                    <Select value={filterStore} onChange={e => setFilterStore(e.target.value)}>
                        <option value="all">כל החנויות</option>
                        {mockStores.map(store => (
                            <option key={store.id} value={store.id}>{store.name}</option>
                        ))}
                    </Select>
                </Filters>

                <Table>
                    <thead>
                        <tr>
                            <Th>משתמש</Th>
                            <Th>תפקיד</Th>
                            <Th>חנות</Th>
                            <Th>טלפון</Th>
                            <Th>סטטוס</Th>
                            <Th>פעולות</Th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredUsers.map(user => (
                            <tr key={user.id}>
                                <Td>
                                    <UserInfo>
                                        <Avatar>{getInitials(user.name)}</Avatar>
                                        <UserDetails>
                                            <UserName>{user.name}</UserName>
                                            <UserEmail>{user.email}</UserEmail>
                                        </UserDetails>
                                    </UserInfo>
                                </Td>
                                <Td>
                                    <RoleBadge $role={user.role}>
                                        {roleLabels[user.role]}
                                    </RoleBadge>
                                </Td>
                                <Td>{user.storeName || '-'}</Td>
                                <Td>{user.phone}</Td>
                                <Td>
                                    <StatusBadge $active={user.isActive}>
                                        {user.isActive ? 'פעיל' : 'לא פעיל'}
                                    </StatusBadge>
                                </Td>
                                <Td>
                                    <Actions>
                                        <ActionButton onClick={() => alert('עריכה (בפיתוח)')}>
                                            ערוך
                                        </ActionButton>
                                        <ActionButton onClick={() => toggleUserStatus(user.id)}>
                                            {user.isActive ? 'השבת' : 'הפעל'}
                                        </ActionButton>
                                    </Actions>
                                </Td>
                            </tr>
                        ))}
                    </tbody>
                </Table>

                {/* Create User Modal */}
                {showCreateModal && (
                    <Modal onClick={() => setShowCreateModal(false)}>
                        <ModalContent onClick={e => e.stopPropagation()}>
                            <ModalTitle>יצירת משתמש חדש</ModalTitle>

                            <FormGroup>
                                <Label>שם מלא *</Label>
                                <Input
                                    type="text"
                                    value={newUser.name}
                                    onChange={e => setNewUser({ ...newUser, name: e.target.value })}
                                    placeholder="ישראל ישראלי"
                                />
                            </FormGroup>

                            <FormGroup>
                                <Label>אימייל *</Label>
                                <Input
                                    type="email"
                                    value={newUser.email}
                                    onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                                    placeholder="israel@store.com"
                                />
                            </FormGroup>

                            <FormGroup>
                                <Label>טלפון</Label>
                                <Input
                                    type="tel"
                                    value={newUser.phone}
                                    onChange={e => setNewUser({ ...newUser, phone: e.target.value })}
                                    placeholder="054-1234567"
                                />
                            </FormGroup>

                            {isChainAdmin && (
                                <FormGroup>
                                    <Label>תפקיד *</Label>
                                    <FormSelect
                                        value={newUser.role}
                                        onChange={e => setNewUser({ ...newUser, role: e.target.value as 'MANAGER' | 'SELLER' })}
                                    >
                                        <option value="SELLER">מוכר</option>
                                        <option value="MANAGER">מנהל חנות</option>
                                    </FormSelect>
                                </FormGroup>
                            )}

                            <FormGroup>
                                <Label>חנות *</Label>
                                <FormSelect
                                    value={newUser.storeId}
                                    onChange={e => setNewUser({ ...newUser, storeId: e.target.value })}
                                >
                                    <option value="">בחר חנות...</option>
                                    {mockStores.map(store => (
                                        <option key={store.id} value={store.id}>{store.name}</option>
                                    ))}
                                </FormSelect>
                            </FormGroup>

                            <ModalActions>
                                <Button $variant="secondary" onClick={() => setShowCreateModal(false)}>
                                    ביטול
                                </Button>
                                <Button
                                    onClick={handleCreateUser}
                                    disabled={!newUser.name || !newUser.email || !newUser.storeId}
                                >
                                    צור משתמש
                                </Button>
                            </ModalActions>
                        </ModalContent>
                    </Modal>
                )}
            </Container>
        </Layout>
    );
}
