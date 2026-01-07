import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Subtitle = styled.p`
  color: ${theme.colors.textSecondary};
  margin: 0;
`;

const Filters = styled.div`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xl};
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${theme.spacing.md};
`;

const FilterGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
`;

const Label = styled.label`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const Input = styled.input`
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

const Actions = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  align-items: flex-end;
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  background: ${props => props.$variant === 'secondary' ? theme.colors.surface : theme.colors.primary};
  color: ${props => props.$variant === 'secondary' ? theme.colors.text : 'white'};
  border: 1px solid ${props => props.$variant === 'secondary' ? theme.colors.border : theme.colors.primary};
  border-radius: ${theme.borderRadius.md};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${props => props.$variant === 'secondary' ? theme.colors.backgroundAlt : theme.colors.primaryDark};
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

const Thead = styled.thead`
  background: ${theme.colors.backgroundAlt};
`;

const Th = styled.th`
  padding: ${theme.spacing.md};
  text-align: right;
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  border-bottom: 1px solid ${theme.colors.border};
`;

const Tbody = styled.tbody``;

const Tr = styled.tr`
  &:hover {
    background: ${theme.colors.backgroundAlt};
  }
  
  &:not(:last-child) {
    border-bottom: 1px solid ${theme.colors.border};
  }
`;

const Td = styled.td`
  padding: ${theme.spacing.md};
  color: ${theme.colors.text};
`;

const Status = styled.span<{ $status: string }>`
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  background: ${props => {
        switch (props.$status) {
            case 'completed': return theme.colors.successLight;
            case 'pending': return theme.colors.warningLight;
            case 'failed': return theme.colors.errorLight;
            default: return theme.colors.gray[100];
        }
    }};
  color: ${props => {
        switch (props.$status) {
            case 'completed': return theme.colors.successDark;
            case 'pending': return theme.colors.warningDark;
            case 'failed': return theme.colors.errorDark;
            default: return theme.colors.gray[700];
        }
    }};
`;

const Amount = styled.span<{ $type: 'income' | 'expense' }>`
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${props => props.$type === 'income' ? theme.colors.success : theme.colors.error};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing['3xl']};
  color: ${theme.colors.textSecondary};
`;

const RoleInfo = styled.div`
  background: ${theme.colors.infoLight};
  border: 1px solid ${theme.colors.info};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
  color: ${theme.colors.infoDark};
  font-size: ${theme.typography.fontSize.sm};
`;

interface Transaction {
    id: string;
    date: string;
    time: string;
    customer: string;
    amount: number;
    status: 'completed' | 'pending' | 'failed';
    items: number;
    paymentMethod: string;
}

/**
 * TransactionsPage - Full transaction management
 * 
 * Role-based access:
 * - CUSTOMER: Own transactions only
 * - CASHIER: Today's transactions
 * - MANAGER: All transactions + filters
 * - ADMIN: All + export + delete
 */
export function TransactionsPage() {
    const { userRole } = useAuth();
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    // Mock data - replace with API call
    const [transactions] = useState<Transaction[]>([
        { id: 'TXN-001', date: '2026-01-07', time: '10:30', customer: 'לקוח א', amount: 450, status: 'completed', items: 3, paymentMethod: 'אשראי' },
        { id: 'TXN-002', date: '2026-01-07', time: '11:15', customer: 'לקוח ב', amount: 280, status: 'completed', items: 2, paymentMethod: 'מזומן' },
        { id: 'TXN-003', date: '2026-01-07', time: '12:00', customer: 'לקוח ג', amount: 620, status: 'pending', items: 5, paymentMethod: 'אשראי' },
        { id: 'TXN-004', date: '2026-01-06', time: '13:45', customer: 'לקוח ד', amount: 150, status: 'completed', items: 1, paymentMethod: 'מזומן' },
        { id: 'TXN-005', date: '2026-01-06', time: '14:20', customer: 'לקוח ה', amount: 890, status: 'failed', items: 4, paymentMethod: 'אשראי' },
    ]);

    const getRolePermissions = () => {
        switch (userRole) {
            case 'ADMIN':
                return { canExport: true, canDelete: true, canViewAll: true, canFilter: true };
            case 'MANAGER':
                return { canExport: true, canDelete: false, canViewAll: true, canFilter: true };
            case 'CASHIER':
                return { canExport: false, canDelete: false, canViewAll: false, canFilter: false };
            default: // CUSTOMER
                return { canExport: false, canDelete: false, canViewAll: false, canFilter: false };
        }
    };

    const permissions = getRolePermissions();

    const filteredTransactions = transactions.filter(txn => {
        if (!permissions.canViewAll && txn.date !== '2026-01-07') return false;
        if (searchTerm && !txn.id.toLowerCase().includes(searchTerm.toLowerCase()) &&
            !txn.customer.includes(searchTerm)) return false;
        if (statusFilter !== 'all' && txn.status !== statusFilter) return false;
        if (dateFrom && txn.date < dateFrom) return false;
        if (dateTo && txn.date > dateTo) return false;
        return true;
    });

    const handleExport = () => {
        alert('ייצוא ל-CSV (בפיתוח)');
    };

    const getRoleMessage = () => {
        switch (userRole) {
            case 'ADMIN':
                return 'מנהל מערכת: גישה מלאה לכל הטרנזקציות + ייצוא + מחיקה';
            case 'MANAGER':
                return 'מנהל: גישה לכל הטרנזקציות + ייצוא + פילטרים';
            case 'CASHIER':
                return 'קופאי: גישה לטרנזקציות של היום בלבד';
            default:
                return 'לקוח: גישה לטרנזקציות שלך בלבד';
        }
    };

    return (
        <Layout>
            <Container>
                <Header>
                    <Title>ניהול טרנזקציות</Title>
                    <Subtitle>צפייה וניהול של כל העסקאות במערכת</Subtitle>
                </Header>

                <RoleInfo>
                    {getRoleMessage()}
                </RoleInfo>

                {permissions.canFilter && (
                    <Filters>
                        <FilterGroup>
                            <Label>חיפוש</Label>
                            <Input
                                type="text"
                                placeholder="מספר טרנזקציה או לקוח..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </FilterGroup>

                        <FilterGroup>
                            <Label>סטטוס</Label>
                            <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                                <option value="all">הכל</option>
                                <option value="completed">הושלם</option>
                                <option value="pending">ממתין</option>
                                <option value="failed">נכשל</option>
                            </Select>
                        </FilterGroup>

                        <FilterGroup>
                            <Label>מתאריך</Label>
                            <Input
                                type="date"
                                value={dateFrom}
                                onChange={(e) => setDateFrom(e.target.value)}
                            />
                        </FilterGroup>

                        <FilterGroup>
                            <Label>עד תאריך</Label>
                            <Input
                                type="date"
                                value={dateTo}
                                onChange={(e) => setDateTo(e.target.value)}
                            />
                        </FilterGroup>

                        <Actions>
                            {permissions.canExport && (
                                <Button onClick={handleExport}>ייצוא CSV</Button>
                            )}
                            <Button $variant="secondary" onClick={() => {
                                setSearchTerm('');
                                setStatusFilter('all');
                                setDateFrom('');
                                setDateTo('');
                            }}>
                                נקה
                            </Button>
                        </Actions>
                    </Filters>
                )}

                {filteredTransactions.length > 0 ? (
                    <Table>
                        <Thead>
                            <Tr>
                                <Th>מספר</Th>
                                <Th>תאריך</Th>
                                <Th>שעה</Th>
                                <Th>לקוח</Th>
                                <Th>פריטים</Th>
                                <Th>אמצעי תשלום</Th>
                                <Th>סכום</Th>
                                <Th>סטטוס</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {filteredTransactions.map((txn) => (
                                <Tr key={txn.id}>
                                    <Td>{txn.id}</Td>
                                    <Td>{txn.date}</Td>
                                    <Td>{txn.time}</Td>
                                    <Td>{txn.customer}</Td>
                                    <Td>{txn.items}</Td>
                                    <Td>{txn.paymentMethod}</Td>
                                    <Td>
                                        <Amount $type="income">₪{txn.amount.toLocaleString()}</Amount>
                                    </Td>
                                    <Td>
                                        <Status $status={txn.status}>
                                            {txn.status === 'completed' ? 'הושלם' :
                                                txn.status === 'pending' ? 'ממתין' : 'נכשל'}
                                        </Status>
                                    </Td>
                                </Tr>
                            ))}
                        </Tbody>
                    </Table>
                ) : (
                    <EmptyState>לא נמצאו טרנזקציות</EmptyState>
                )}
            </Container>
        </Layout>
    );
}
