import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { theme } from '@/styles/theme';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: calc(100vh - 64px);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.xl};
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
  margin: 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const DateFilter = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
`;

const FilterButton = styled.button<{ $active?: boolean }>`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${props => props.$active ? theme.colors.primary : theme.colors.border};
  background: ${props => props.$active ? theme.colors.primary : 'white'};
  color: ${props => props.$active ? 'white' : theme.colors.text};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    border-color: ${theme.colors.primary};
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xl};

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

const StatCard = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.sm};
  transition: all ${theme.transitions.base};
  border-top: 4px solid ${theme.colors.primary};
  animation: ${theme.animations.slideUp};
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: ${theme.shadows.lg};
  }
`;

const StatLabel = styled.div`
  font-size: ${theme.typography.fontSize.xs};
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.xs};
`;

const StatValue = styled.div`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  letter-spacing: -0.02em;
`;

const StatChange = styled.span<{ $positive?: boolean }>`
  font-size: ${theme.typography.fontSize.xs};
  color: ${props => props.$positive ? theme.colors.success : theme.colors.error};
  display: flex;
  align-items: center;
  gap: 2px;
  margin-top: ${theme.spacing.xs};
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xl};

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.sm};
`;

const ChartTitle = styled.h3`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.lg} 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const FullWidthChart = styled(ChartCard)`
  grid-column: 1 / -1;
`;

const TableCard = styled(ChartCard)``;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const Th = styled.th`
  text-align: right;
  padding: ${theme.spacing.sm};
  border-bottom: 2px solid ${theme.colors.border};
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const Td = styled.td`
  text-align: right;
  padding: ${theme.spacing.sm};
  border-bottom: 1px solid ${theme.colors.border};
  font-size: ${theme.typography.fontSize.sm};
`;

const MaterialIcon = ({ name, size = 24 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

const COLORS = ['#1E293B', '#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

export function StoreBIPage() {
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month' | 'year'>('week');

  const salesData = [
    { name: 'ראשון', sales: 0, revenue: 0 },
    { name: 'שני', sales: 0, revenue: 0 },
    { name: 'שלישי', sales: 0, revenue: 0 },
    { name: 'רביעי', sales: 0, revenue: 0 },
    { name: 'חמישי', sales: 0, revenue: 0 },
    { name: 'שישי', sales: 0, revenue: 0 },
    { name: 'שבת', sales: 0, revenue: 0 },
  ];

  const categoryData = [
    { name: 'אלקטרוניקה', value: 0 },
    { name: 'ביגוד', value: 0 },
    { name: 'מזון', value: 0 },
    { name: 'אחר', value: 0 },
  ];

  const hourlyData = Array.from({ length: 12 }, (_, i) => ({
    hour: `${8 + i}:00`,
    customers: 0,
    sales: 0,
  }));

  const topProducts: { name: string; sold: number; revenue: number }[] = [];

  const stats = {
    totalRevenue: 0,
    totalSales: 0,
    avgTransaction: 0,
    customers: 0,
  };

  return (
    <Layout>
      <Container>
        <Header>
          <Title>
            <MaterialIcon name="analytics" />
            דוחות וניתוחים
          </Title>
          <DateFilter>
            <FilterButton $active={dateRange === 'today'} onClick={() => setDateRange('today')}>
              היום
            </FilterButton>
            <FilterButton $active={dateRange === 'week'} onClick={() => setDateRange('week')}>
              שבוע
            </FilterButton>
            <FilterButton $active={dateRange === 'month'} onClick={() => setDateRange('month')}>
              חודש
            </FilterButton>
            <FilterButton $active={dateRange === 'year'} onClick={() => setDateRange('year')}>
              שנה
            </FilterButton>
          </DateFilter>
        </Header>

        <StatsGrid>
            <StatCard style={{ borderTop: `4px solid #1E293B` }}>
              <StatLabel>הכנסות כוללות</StatLabel>
              <StatValue>{stats.totalRevenue.toLocaleString()} ש"ח</StatValue>
              <StatChange $positive>אין נתונים להשוואה</StatChange>
            </StatCard>
            <StatCard style={{ borderTop: `4px solid #3B82F6` }}>
              <StatLabel>מספר עסקאות</StatLabel>
              <StatValue>{stats.totalSales}</StatValue>
              <StatChange $positive>אין נתונים להשוואה</StatChange>
            </StatCard>
            <StatCard style={{ borderTop: `4px solid #10B981` }}>
              <StatLabel>ממוצע לעסקה</StatLabel>
              <StatValue>{stats.avgTransaction.toLocaleString()} ש"ח</StatValue>
              <StatChange $positive>אין נתונים להשוואה</StatChange>
            </StatCard>
            <StatCard style={{ borderTop: `4px solid #F59E0B` }}>
              <StatLabel>לקוחות</StatLabel>
              <StatValue>{stats.customers}</StatValue>
              <StatChange $positive>אין נתונים להשוואה</StatChange>
            </StatCard>
        </StatsGrid>

        <ChartsGrid>
          <ChartCard>
            <ChartTitle>
              <MaterialIcon name="trending_up" size={20} />
              מגמת מכירות
            </ChartTitle>
            {salesData.every(d => d.sales === 0) ? (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.colors.textSecondary }}>
                <div style={{ textAlign: 'center' }}>
                  <MaterialIcon name="bar_chart" size={48} />
                  <div>אין נתוני מכירות</div>
                </div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={salesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="revenue" stroke={theme.colors.primary} fill={theme.colors.primary + '40'} name="הכנסות" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </ChartCard>

          <ChartCard>
            <ChartTitle>
              <MaterialIcon name="pie_chart" size={20} />
              התפלגות לפי קטגוריה
            </ChartTitle>
            {categoryData.every(d => d.value === 0) ? (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.colors.textSecondary }}>
                <div style={{ textAlign: 'center' }}>
                  <MaterialIcon name="donut_large" size={48} />
                  <div>אין נתוני קטגוריות</div>
                </div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }: { name: string; percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {categoryData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </ChartCard>
        </ChartsGrid>

        <ChartsGrid>
          <FullWidthChart>
            <ChartTitle>
              <MaterialIcon name="schedule" size={20} />
              פעילות לפי שעות
            </ChartTitle>
            {hourlyData.every(d => d.customers === 0) ? (
              <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.colors.textSecondary }}>
                <div style={{ textAlign: 'center' }}>
                  <MaterialIcon name="timeline" size={48} />
                  <div>אין נתוני פעילות</div>
                </div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis yAxisId="left" orientation="right" />
                  <YAxis yAxisId="right" orientation="left" />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="customers" fill={theme.colors.info} name="לקוחות" />
                  <Bar yAxisId="right" dataKey="sales" fill={theme.colors.success} name="מכירות" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </FullWidthChart>
        </ChartsGrid>

        <TableCard>
          <ChartTitle>
            <MaterialIcon name="star" size={20} />
            מוצרים מובילים
          </ChartTitle>
          {topProducts.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: theme.colors.textSecondary }}>
              <MaterialIcon name="inventory_2" size={48} />
              <div>אין נתוני מוצרים</div>
            </div>
          ) : (
            <Table>
              <thead>
                <tr>
                  <Th>מוצר</Th>
                  <Th>יחידות נמכרו</Th>
                  <Th>הכנסות</Th>
                </tr>
              </thead>
              <tbody>
                {topProducts.map((product, index) => (
                  <tr key={index}>
                    <Td>{product.name}</Td>
                    <Td>{product.sold}</Td>
                    <Td>{product.revenue.toLocaleString()} ש"ח</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </TableCard>
      </Container>
    </Layout>
  );
}
