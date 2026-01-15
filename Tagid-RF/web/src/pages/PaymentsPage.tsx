import { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.xl};
  animation: ${fadeIn} 0.4s ease-out;
  background: white;
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.sm};
  border-right: 6px solid ${theme.colors.primary};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
`;

const Subtitle = styled.p`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  margin: ${theme.spacing.xs} 0 0 0;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xl};
  animation: ${fadeIn} 0.5s ease-out;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.sm};
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid ${theme.colors.borderLight};
`;

const CardTitle = styled.h2`
  font-size: 1rem;
  font-weight: 600;
  color: ${theme.colors.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Button = styled.button<{ $variant?: 'primary' | 'success' | 'danger' }>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => {
        switch (props.$variant) {
            case 'success': return theme.colors.success;
            case 'danger': return theme.colors.error;
            default: return theme.colors.primary;
        }
    }};
  color: white;
  
  &:hover:not(:disabled) {
    opacity: 0.9;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SmallButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.4rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.8rem;
  background: white;
  color: ${theme.colors.textSecondary};
  cursor: pointer;
  
  &:hover {
    background: #f8fafc;
  }
`;

// Stats Cards
const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
  
  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
`;

const StatCard = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: ${theme.shadows.sm};
  transition: all ${theme.transitions.base};
  border-top: 4px solid ${theme.colors.primary};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${theme.shadows.md};
  }
`;

const StatLabel = styled.div`
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  color: ${theme.colors.textSecondary};
  margin-bottom: 0.5rem;
`;

const StatValue = styled.div`
  font-size: 1.75rem;
  font-weight: 700;
  color: ${theme.colors.text};
  letter-spacing: -0.02em;
`;

const StatTrend = styled.span<{ $positive: boolean }>`
  font-size: 0.8rem;
  font-weight: 500;
  color: ${props => props.$positive ? theme.colors.success : theme.colors.error};
  margin-top: 0.5rem;
  display: block;
`;

// Bank Account List
const AccountList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const AccountItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
`;

const AccountInfo = styled.div``;

const AccountName = styled.div`
  font-weight: 600;
  color: ${theme.colors.text};
`;

const AccountNumber = styled.div`
  font-size: 0.85rem;
  color: ${theme.colors.textSecondary};
  font-family: monospace;
`;

const AccountBalance = styled.div<{ $positive: boolean }>`
  font-size: 1.1rem;
  font-weight: 700;
  color: ${props => props.$positive ? theme.colors.success : theme.colors.error};
`;

// Transaction List
const TransactionList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
`;

const TransactionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
  
  &:hover {
    background: #f1f5f9;
  }
`;

const TransactionInfo = styled.div``;

const TransactionDesc = styled.div`
  font-weight: 500;
  font-size: 0.9rem;
  color: ${theme.colors.text};
`;

const TransactionMeta = styled.div`
  font-size: 0.8rem;
  color: ${theme.colors.textSecondary};
`;

const TransactionAmount = styled.div<{ $type: 'income' | 'expense' }>`
  font-weight: 700;
  color: ${props => props.$type === 'income' ? theme.colors.success : theme.colors.error};
`;

const StatusBadge = styled.span<{ $status: string }>`
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  background: ${props => {
        switch (props.$status) {
            case 'verified': return '#dcfce7';
            case 'pending': return '#fef3c7';
            case 'failed': return '#fee2e2';
            default: return '#f1f5f9';
        }
    }};
  color: ${props => {
        switch (props.$status) {
            case 'verified': return '#166534';
            case 'pending': return '#92400e';
            case 'failed': return '#991b1b';
            default: return theme.colors.textSecondary;
        }
    }};
  margin-right: 0.5rem;
`;

// Modal
const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
`;

const ModalTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${theme.colors.text};
  margin: 0 0 1.5rem 0;
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
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
`;

const ModalActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
`;

// Types
interface BankAccount {
    id: string;
    name: string;
    bankName: string;
    accountNumber: string;
    branch: string;
    balance: number;
    isDefault: boolean;
}

interface Transaction {
    id: string;
    description: string;
    amount: number;
    type: 'income' | 'expense';
    date: string;
    time: string;
    status: 'verified' | 'pending' | 'failed';
    paymentMethod: string;
}

export function PaymentsPage() {
    const { userRole } = useAuth();
    const [showAddAccount, setShowAddAccount] = useState(false);
    const [accounts, setAccounts] = useState<BankAccount[]>([]);

    const [transactions] = useState<Transaction[]>([]);

    const [newAccount, setNewAccount] = useState({
        name: '',
        bankName: '',
        accountNumber: '',
        branch: '',
    });

    const stats = {
        totalBalance: accounts.reduce((sum, a) => sum + a.balance, 0),
        monthlyIncome: 0,
        monthlyExpense: 0,
        pendingVerification: transactions.filter(t => t.status === 'pending').length,
    };

    const handleAddAccount = () => {
        const account: BankAccount = {
            id: Date.now().toString(),
            ...newAccount,
            balance: 0,
            isDefault: false,
        };
        setAccounts([...accounts, account]);
        setShowAddAccount(false);
        setNewAccount({ name: '', bankName: '', accountNumber: '', branch: '' });
    };

    const handleVerifyTransaction = async (transactionId: string) => {
        // In a real app, this would call the backend API
        console.log('Verifying transaction:', transactionId);
        alert(`עסקה ${transactionId} אומתה בהצלחה`);
    };

    const canManage = userRole === 'SUPER_ADMIN' || userRole === 'NETWORK_ADMIN' || userRole === 'STORE_MANAGER';

    if (!canManage) {
        return (
            <Layout>
                <Container>
                    <div style={{ textAlign: 'center', padding: '4rem' }}>
                        <h2>אין הרשאה</h2>
                        <p>רק מנהלים יכולים לגשת לדף זה</p>
                    </div>
                </Container>
            </Layout>
        );
    }

    return (
        <Layout>
            <Container>
                <Header>
                    <div>
                        <Title>ניהול תשלומים</Title>
                        <Subtitle>חשבונות בנק, אימות עסקאות, ומעקב פיננסי</Subtitle>
                    </div>
                    <Button onClick={() => setShowAddAccount(true)}>
                        <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>add</span>
                        הוסף חשבון
                    </Button>
                </Header>

                {/* Stats */}
                <StatsGrid>
                    <StatCard>
                        <StatLabel>סה"כ יתרה</StatLabel>
                        <StatValue>₪{stats.totalBalance.toLocaleString()}</StatValue>
                        <StatTrend $positive={true}>אין נתונים להשוואה</StatTrend>
                    </StatCard>
                    <StatCard>
                        <StatLabel>הכנסות החודש</StatLabel>
                        <StatValue style={{ color: theme.colors.success }}>₪{stats.monthlyIncome.toLocaleString()}</StatValue>
                    </StatCard>
                    <StatCard>
                        <StatLabel>הוצאות החודש</StatLabel>
                        <StatValue style={{ color: theme.colors.error }}>₪{stats.monthlyExpense.toLocaleString()}</StatValue>
                    </StatCard>
                    <StatCard>
                        <StatLabel>ממתינות לאימות</StatLabel>
                        <StatValue style={{ color: theme.colors.warning }}>{stats.pendingVerification}</StatValue>
                    </StatCard>
                </StatsGrid>

                {/* Main Content */}
                <Grid>
                    {/* Bank Accounts */}
                    <Card>
                        <CardHeader>
                            <CardTitle>
                                <span className="material-symbols-outlined">account_balance</span>
                                חשבונות בנק
                            </CardTitle>
                        </CardHeader>
                        <AccountList>
                            {accounts.map(account => (
                                <AccountItem key={account.id}>
                                    <AccountInfo>
                                        <AccountName>
                                            {account.name}
                                            {account.isDefault && <StatusBadge $status="verified">ברירת מחדל</StatusBadge>}
                                        </AccountName>
                                        <AccountNumber>{account.bankName} • {account.accountNumber}</AccountNumber>
                                    </AccountInfo>
                                    <AccountBalance $positive={account.balance > 0}>
                                        ₪{account.balance.toLocaleString()}
                                    </AccountBalance>
                                </AccountItem>
                            ))}
                        </AccountList>
                    </Card>

                    {/* Recent Transactions */}
                    <Card>
                        <CardHeader>
                            <CardTitle>📋 עסקאות אחרונות</CardTitle>
                            <SmallButton>צפה בכל</SmallButton>
                        </CardHeader>
                        <TransactionList>
                            {transactions.map(txn => (
                                <TransactionItem key={txn.id}>
                                    <TransactionInfo>
                                        <TransactionDesc>
                                            <StatusBadge $status={txn.status}>
                                                {txn.status === 'verified' ? 'מאומת' : txn.status === 'pending' ? 'ממתין' : 'נכשל'}
                                            </StatusBadge>
                                            {txn.description}
                                        </TransactionDesc>
                                        <TransactionMeta>{txn.date} • {txn.time} • {txn.paymentMethod}</TransactionMeta>
                                    </TransactionInfo>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <TransactionAmount $type={txn.type}>
                                            {txn.type === 'income' ? '+' : '-'}₪{txn.amount}
                                        </TransactionAmount>
                                        {txn.status === 'pending' && (
                                            <SmallButton onClick={() => handleVerifyTransaction(txn.id)}>
                                                ✓ אמת
                                            </SmallButton>
                                        )}
                                    </div>
                                </TransactionItem>
                            ))}
                        </TransactionList>
                    </Card>
                </Grid>

                {/* Add Account Modal */}
                {showAddAccount && (
                    <Modal onClick={() => setShowAddAccount(false)}>
                        <ModalContent onClick={e => e.stopPropagation()}>
                            <ModalTitle>הוסף חשבון בנק</ModalTitle>
                            <FormGroup>
                                <Label>שם החשבון</Label>
                                <Input
                                    value={newAccount.name}
                                    onChange={e => setNewAccount({ ...newAccount, name: e.target.value })}
                                    placeholder="לדוגמה: חשבון ראשי"
                                />
                            </FormGroup>
                            <FormGroup>
                                <Label>בנק</Label>
                                <Select
                                    value={newAccount.bankName}
                                    onChange={e => setNewAccount({ ...newAccount, bankName: e.target.value })}
                                >
                                    <option value="">בחר בנק...</option>
                                    <option value="בנק לאומי">בנק לאומי</option>
                                    <option value="בנק הפועלים">בנק הפועלים</option>
                                    <option value="בנק דיסקונט">בנק דיסקונט</option>
                                    <option value="בנק מזרחי">בנק מזרחי טפחות</option>
                                </Select>
                            </FormGroup>
                            <FormGroup>
                                <Label>מספר חשבון</Label>
                                <Input
                                    value={newAccount.accountNumber}
                                    onChange={e => setNewAccount({ ...newAccount, accountNumber: e.target.value })}
                                    placeholder="XX-XXX-XXXXXX"
                                />
                            </FormGroup>
                            <FormGroup>
                                <Label>סניף</Label>
                                <Input
                                    value={newAccount.branch}
                                    onChange={e => setNewAccount({ ...newAccount, branch: e.target.value })}
                                    placeholder="מספר סניף"
                                />
                            </FormGroup>
                            <ModalActions>
                                <Button $variant="danger" onClick={() => setShowAddAccount(false)}>
                                    ביטול
                                </Button>
                                <Button $variant="success" onClick={handleAddAccount}>
                                    שמור
                                </Button>
                            </ModalActions>
                        </ModalContent>
                    </Modal>
                )}
            </Container>
        </Layout>
    );
}
