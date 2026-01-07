import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { StatCard } from '@/components/Dashboard/StatCard';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';
import { slideInUp } from '@/styles/animations';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['4xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  background: ${theme.colors.primaryGradient};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Subtitle = styled.p`
  font-size: ${theme.typography.fontSize.lg};
  color: ${theme.colors.textSecondary};
  margin: 0;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xl};
  animation: ${slideInUp} 0.5s ease-out;
`;

const Section = styled.section`
  background: ${theme.colors.surface};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  box-shadow: ${theme.shadows.md};
  margin-bottom: ${theme.spacing.xl};
  animation: ${slideInUp} 0.6s ease-out;
`;

const SectionTitle = styled.h2`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  margin: 0 0 ${theme.spacing.lg} 0;
  color: ${theme.colors.text};
`;

const TransactionList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const TransactionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${theme.spacing.md};
  background: ${theme.colors.backgroundAlt};
  border-radius: ${theme.borderRadius.lg};
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${theme.colors.gray[100]};
    transform: translateX(4px);
  }
`;

const TransactionInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
`;

const TransactionId = styled.span`
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const TransactionTime = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const TransactionAmount = styled.span<{ $type: 'income' | 'expense' }>`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${props => props.$type === 'income' ? theme.colors.success : theme.colors.error};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing['3xl']};
  color: ${theme.colors.textSecondary};
`;

const RoleBadge = styled.span<{ $role: string }>`
  display: inline-block;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  background: ${props => {
    switch (props.$role) {
      case 'ADMIN': return theme.colors.accent.purple;
      case 'MANAGER': return theme.colors.accent.blue;
      case 'CASHIER': return theme.colors.accent.green;
      default: return theme.colors.gray[400];
    }
  }};
  color: white;
  margin-bottom: ${theme.spacing.md};
`;

const LogoutButton = styled.button`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }
`;

const HeaderTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: ${theme.spacing.md};
`;

/**
 * DashboardPage - Main business dashboard
 * 
 * Shows sales overview, revenue, transactions, and role-specific content
 */
export function DashboardPage() {
  const { userRole, logout } = useAuth();
  const [stats] = useState({
    revenue: 15420,
    sales: 48,
    items: 156,
    avgTransaction: 321,
  });

  const [recentTransactions] = useState([
    { id: 'TXN-001', amount: 450, time: '10:30', type: 'income' as const },
    { id: 'TXN-002', amount: 280, time: '11:15', type: 'income' as const },
    { id: 'TXN-003', amount: 620, time: '12:00', type: 'income' as const },
    { id: 'TXN-004', amount: 150, time: '13:45', type: 'income' as const },
    { id: 'TXN-005', amount: 890, time: '14:20', type: 'income' as const },
  ]);

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'ADMIN': return theme.colors.error; // Red
      case 'MANAGER': return theme.colors.primary; // Blue
      case 'CASHIER': return theme.colors.success; // Green
      default: return theme.colors.gray[600]; // Gray
    }
  };

  const getRoleName = (role: string) => {
    switch (role) {
      case 'ADMIN': return 'מנהל מערכת';
      case 'MANAGER': return 'מנהל';
      case 'CASHIER': return 'קופאי';
      default: return 'לקוח';
    }
  };

  return (
    <Layout>
      <Container>
        <Header>
          <HeaderTop>
            <div>
              <RoleBadge $role={userRole || 'CUSTOMER'} style={{ background: getRoleColor(userRole || 'CUSTOMER') }}>
                {getRoleName(userRole || 'CUSTOMER')}
              </RoleBadge>
              <Title>דשבורד מכירות</Title>
              <Subtitle>סקירה כללית של העסק שלך</Subtitle>
            </div>
            <LogoutButton onClick={logout}>
              התנתק
            </LogoutButton>
          </HeaderTop>
        </Header>

        <StatsGrid>
          <StatCard
            title="הכנסות היום"
            value={`₪${stats.revenue.toLocaleString()}`}
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            title="מכירות"
            value={stats.sales}
            trend={{ value: 8, isPositive: true }}
          />
          <StatCard
            title="פריטים נמכרו"
            value={stats.items}
            trend={{ value: 5, isPositive: false }}
          />
          <StatCard
            title="ממוצע טרנזקציה"
            value={`₪${stats.avgTransaction}`}
            trend={{ value: 15, isPositive: true }}
          />
        </StatsGrid>

        <Section>
          <SectionTitle>טרנזקציות אחרונות</SectionTitle>
          {recentTransactions.length > 0 ? (
            <TransactionList>
              {recentTransactions.map(txn => (
                <TransactionItem key={txn.id}>
                  <TransactionInfo>
                    <TransactionId>{txn.id}</TransactionId>
                    <TransactionTime>{txn.time}</TransactionTime>
                  </TransactionInfo>
                  <TransactionAmount $type={txn.type}>
                    ₪{txn.amount.toLocaleString()}
                  </TransactionAmount>
                </TransactionItem>
              ))}
            </TransactionList>
          ) : (
            <EmptyState>אין טרנזקציות להצגה</EmptyState>
          )}
        </Section>

        {/* Role-specific content */}
        {(userRole === 'ADMIN' || userRole === 'MANAGER') && (
          <Section>
            <SectionTitle>תוכן למנהלים בלבד</SectionTitle>
            <p style={{ color: theme.colors.textSecondary }}>
              כאן יופיעו דוחות מתקדמים, ניהול משתמשים, והגדרות מערכת
            </p>
          </Section>
        )}

        {userRole === 'ADMIN' && (
          <Section>
            <SectionTitle>תוכן למנהל מערכת בלבד</SectionTitle>
            <p style={{ color: theme.colors.textSecondary }}>
              הגדרות מתקדמות, ניהול הרשאות, ולוגים של המערכת
            </p>
          </Section>
        )}
      </Container>
    </Layout>
  );
}
