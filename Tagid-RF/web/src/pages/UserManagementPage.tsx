import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: calc(100vh - 64px);
  animation: ${theme.animations.fadeIn};
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.xl};
  flex-wrap: wrap;
  gap: ${theme.spacing.md};
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.lg};
  border-right: 10px solid #1E3A8A;
  color: white;
  animation: ${theme.animations.slideUp};

  h1, p {
    color: white;
  }
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const Subtitle = styled.p`
  color: ${theme.colors.textSecondary};
  margin: 0;
  font-size: ${theme.typography.fontSize.sm};
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' | 'danger' }>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  background: ${props => {
    switch (props.$variant) {
      case 'secondary': return 'white';
      case 'danger': return theme.colors.error;
      default: return theme.colors.primaryGradient;
    }
  }};
  color: ${props => props.$variant === 'secondary' ? theme.colors.text : 'white'};
  border: 1px solid ${props => {
    switch (props.$variant) {
      case 'secondary': return theme.colors.border;
      case 'danger': return theme.colors.error;
      default: return 'transparent';
    }
  }};
  border-radius: ${theme.borderRadius.md};
  font-weight: ${theme.typography.fontWeight.semibold};
  font-size: ${theme.typography.fontSize.base};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  box-shadow: ${props => props.$variant ? 'none' : theme.shadows.sm};

  &:hover {
    transform: translateY(-1px);
    box-shadow: ${props => props.$variant ? theme.shadows.sm : theme.shadows.md};
    opacity: 0.95;
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Filters = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
  flex-wrap: wrap;
  background: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.lg};
  border: 1px solid ${theme.colors.border};
  box-shadow: ${theme.shadows.sm};
`;

const Select = styled.select`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  padding-left: ${theme.spacing.xl};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: white;
  min-width: 150px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='24' viewBox='0 -960 960 960' width='24'%3E%3Cpath d='M480-345 240-585l56-56 184 184 184-184 56 56-240 240Z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left 8px center;
  background-size: 20px;

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
  animation: ${theme.animations.fadeIn};

  tr {
    transition: all ${theme.transitions.fast};
    &:hover {
      background: ${theme.colors.backgroundAlt};
    }
  }
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
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: ${theme.colors.primaryGradient};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: ${theme.typography.fontWeight.bold};
  font-size: ${theme.typography.fontSize.sm};
  box-shadow: ${theme.shadows.sm};
  transition: all ${theme.transitions.base};

  &:hover {
    transform: scale(1.1) rotate(5deg);
    box-shadow: ${theme.shadows.md};
  }
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
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  background: ${props => {
    switch (props.$role) {
      case 'ADMIN': return `${theme.colors.info}15`;
      case 'MANAGER': return `${theme.colors.success}15`;
      case 'SELLER': return `${theme.colors.warning}15`;
      default: return `${theme.colors.gray[100]}`;
    }
  }};
  color: ${props => {
    switch (props.$role) {
      case 'ADMIN': return theme.colors.info;
      case 'MANAGER': return theme.colors.success;
      case 'SELLER': return theme.colors.warning;
      default: return theme.colors.gray[600];
    }
  }};
  border: 1px solid currentColor;
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.bold};
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);

  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
  }
`;

const StatusBadge = styled.span<{ $active: boolean }>`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  background: ${props => props.$active ? '#ECFDF5' : '#F9FAFB'};
  color: ${props => props.$active ? '#059669' : '#6B7280'};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.semibold};

  &::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: ${props => props.$active ? '#10B981' : '#9CA3AF'};
    box-shadow: ${props => props.$active ? '0 0 8px #10B98180' : 'none'};
  }
`;

const Actions = styled.div`
  display: flex;
  gap: ${theme.spacing.xs};
`;

const ActionButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  color: ${theme.colors.textSecondary};
  cursor: pointer;
  transition: all ${theme.transitions.base};

  &:hover {
    background: ${theme.colors.backgroundAlt};
    color: ${theme.colors.primary};
    border-color: ${theme.colors.primary};
    transform: translateY(-2px);
    box-shadow: ${theme.shadows.sm};
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
  padding-left: ${theme.spacing.xl};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: white;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='24' viewBox='0 -960 960 960' width='24'%3E%3Cpath d='M480-345 240-585l56-56 184 184 184-184 56 56-240 240Z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left 8px center;
  background-size: 20px;

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

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing['4xl']} ${theme.spacing.xl};
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  color: ${theme.colors.textSecondary};
  box-shadow: ${theme.shadows.sm};
`;

const EmptyIcon = styled.div`
  width: 80px;
  height: 80px;
  background: ${theme.colors.gray[50]};
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto ${theme.spacing.lg};
  
  .material-symbols-outlined {
    font-size: 40px;
    color: ${theme.colors.gray[300]};
  }
`;

const MaterialIcon = ({ name, size = 20 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

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
    const [users, setUsers] = useState<User[]>([]);
    const [stores] = useState<{ id: string; name: string }[]>([]);
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

    const isSuperAdmin = userRole === 'SUPER_ADMIN';
    const isNetworkAdmin = userRole === 'NETWORK_ADMIN';
    const isStoreManager = userRole === 'STORE_MANAGER';
    const canManageUsers = isSuperAdmin || isNetworkAdmin || isStoreManager;

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
        if (isStoreManager && !isSuperAdmin && !isNetworkAdmin) {
            if (user.role !== 'SELLER') return false;
        }

        if (filterRole !== 'all' && user.role !== filterRole) return false;
        if (filterStore !== 'all' && user.storeId !== filterStore) return false;
        return true;
    });

    const handleCreateUser = () => {
        if (!newUser.name || !newUser.email || !newUser.storeId) return;

        const store = stores.find(s => s.id === newUser.storeId);
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
                    <div>
                        <Title>
                            <MaterialIcon name="group" size={32} />
                            ניהול משתמשים
                        </Title>
                        <Subtitle>
                            {(isSuperAdmin || isNetworkAdmin) ? 'נהל מנהלים ומוכרים בכל החנויות' : 'נהל מוכרים בחנות שלך'}
                        </Subtitle>
                    </div>
                    <Button onClick={() => setShowCreateModal(true)}>
                        <MaterialIcon name="person_add" size={20} />
                        משתמש חדש
                    </Button>
                </Header>

                <Filters>
                    {(isSuperAdmin || isNetworkAdmin) && (
                        <Select value={filterRole} onChange={e => setFilterRole(e.target.value)}>
                            <option value="all">כל התפקידים</option>
                            <option value="MANAGER">מנהלי חנות</option>
                            <option value="SELLER">מוכרים</option>
                        </Select>
                    )}
                    <Select value={filterStore} onChange={e => setFilterStore(e.target.value)}>
                        <option value="all">כל החנויות</option>
                        {stores.map(store => (
                            <option key={store.id} value={store.id}>{store.name}</option>
                        ))}
                    </Select>
                </Filters>

                {filteredUsers.length > 0 ? (
                    <Table>
                        <thead>
                            <tr>
                                <Th>משתמש</Th>
                                <Th>תפקיד</Th>
                                <Th>חנות</Th>
                                <Th>טלפון</Th>
                                <Th>סטטוס</Th>
                                <Th style={{ textAlign: 'center' }}>פעולות</Th>
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
                                    <Td style={{ direction: 'ltr', textAlign: 'right' }}>{user.phone}</Td>
                                    <Td>
                                        <StatusBadge $active={user.isActive}>
                                            {user.isActive ? 'פעיל' : 'לא פעיל'}
                                        </StatusBadge>
                                    </Td>
                                    <Td>
                                        <Actions style={{ justifyContent: 'center' }}>
                                            <ActionButton title="ערוך">
                                                <MaterialIcon name="edit" size={18} />
                                            </ActionButton>
                                            <ActionButton 
                                                onClick={() => toggleUserStatus(user.id)}
                                                title={user.isActive ? 'חסום' : 'שחרר חסימה'}
                                                style={{ color: user.isActive ? theme.colors.error : theme.colors.success }}
                                            >
                                                <MaterialIcon name={user.isActive ? 'block' : 'check_circle'} size={18} />
                                            </ActionButton>
                                        </Actions>
                                    </Td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                ) : (
                    <EmptyState>
                        <EmptyIcon>
                            <MaterialIcon name="group_off" />
                        </EmptyIcon>
                        <Title style={{ fontSize: '1.5rem', justifyContent: 'center', marginBottom: '0.5rem' }}>
                            אין משתמשים במערכת
                        </Title>
                        <Subtitle style={{ textAlign: 'center' }}>הוסף משתמש חדש כדי להתחיל לנהל את הצוות שלך</Subtitle>
                    </EmptyState>
                )}

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

                            {(isSuperAdmin || isNetworkAdmin) && (
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
                                    {stores.map(store => (
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
