import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled, { keyframes } from 'styled-components';
import { Layout } from '@/components/Layout';
import { EmptyState } from '@/components/EmptyState';
import { useTranslation } from '@/hooks/useTranslation';
import { formatCurrency } from '@/lib/utils/currency';
import { theme } from '@/styles/theme';
import { fetchOrders, Order } from '@/api/orders';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  padding: ${theme.spacing.lg};
`;

const PageHeader = styled.div`
  margin-bottom: ${theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: 800;
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.xs} 0;
  letter-spacing: -0.5px;
`;

const Subtitle = styled.p`
  font-size: ${theme.typography.fontSize.base};
  color: ${theme.colors.textSecondary};
  margin: 0;
`;

const OrdersList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.lg};
`;

const OrderCard = styled.div<{ index: number }>`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: 20px;
  padding: ${theme.spacing.xl};
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: ${fadeIn} 0.5s ease forwards;
  animation-delay: ${props => props.index * 0.1}s;
  opacity: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;

  &:hover {
    border-color: ${theme.colors.primary};
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.05);
    transform: translateY(-4px);
  }

  @media (max-width: ${theme.breakpoints.mobile}) {
    flex-direction: column;
    align-items: flex-start;
    gap: ${theme.spacing.lg};
  }
`;

const OrderMainInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.lg};
`;

const StatusIconWrapper = styled.div<{ status: string }>`
  width: 60px;
  height: 60px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props =>
    props.status === 'COMPLETED' ? '#D1FAE5' :
      props.status === 'PENDING' ? '#FEF3C7' :
        '#FEE2E2'};
  color: ${props =>
    props.status === 'COMPLETED' ? '#065F46' :
      props.status === 'PENDING' ? '#92400E' :
        '#991B1B'};
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
`;

const TextGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const OrderNumber = styled.span`
  font-size: 11px;
  color: #64748b;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1.2px;
`;

const DateText = styled.span`
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
`;

const BadgeGroup = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 6px;
`;

const ProviderBadge = styled.span`
  background: #4338CA;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(67, 56, 202, 0.2);
`;

const StatusBadge = styled.span<{ status: string }>`
  background: ${props =>
    props.status === 'COMPLETED' ? '#059669' :
      props.status === 'PENDING' ? '#D97706' :
        '#DC2626'};
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 900;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const OrderPrice = styled.div`
  text-align: right;
  
  @media (max-width: ${theme.breakpoints.mobile}) {
    text-align: left;
    width: 100%;
    border-top: 1px solid ${theme.colors.border};
    padding-top: ${theme.spacing.md};
  }
`;

const Amount = styled.div`
  font-size: 24px;
  font-weight: 800;
  color: ${theme.colors.text};
`;

const ViewDetailsText = styled.div`
  font-size: 12px;
  color: ${theme.colors.primary};
  font-weight: 600;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;

  @media (max-width: ${theme.breakpoints.mobile}) {
    justify-content: flex-start;
  }
`;

const MaterialIcon = ({ name, size = 24 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size, display: 'block' }}>{name}</span>
);

export function OrdersPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders().then(data => {
      setOrders(data.orders);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <Layout><Container>טוען...</Container></Layout>;

  return (
    <Layout>
      <Container>
        <PageHeader>
          <Title>הזמנות שלי</Title>
          <Subtitle>מעקב אחר רכישות ותשלומים</Subtitle>
        </PageHeader>

        <OrdersList>
          {orders.map((order, index) => (
            <OrderCard key={order.id} index={index} onClick={() => navigate(`/orders/${order.id}/success`)}>
              <OrderMainInfo>
                <StatusIconWrapper status={order.status}>
                  <MaterialIcon name={
                    order.status === 'COMPLETED' ? 'check_circle' :
                      order.status === 'PENDING' ? 'update' : 'error'
                  } size={32} />
                </StatusIconWrapper>
                <TextGroup>
                  <OrderNumber>ORDER #{order.id.slice(0, 8)}</OrderNumber>
                  <DateText>
                    {new Date(order.createdAt).toLocaleDateString('he-IL', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </DateText>
                  <BadgeGroup>
                    <ProviderBadge>{order.provider}</ProviderBadge>
                    <StatusBadge status={order.status}>
                      {order.status === 'COMPLETED' ? 'שולם' : order.status === 'PENDING' ? 'ממתין' : 'נכשל'}
                    </StatusBadge>
                  </BadgeGroup>
                </TextGroup>
              </OrderMainInfo>
              <OrderPrice>
                <Amount>{formatCurrency(order.totalInCents)}</Amount>
                <ViewDetailsText>
                  פרטי הזמנה <MaterialIcon name="chevron_left" size={16} />
                </ViewDetailsText>
              </OrderPrice>
            </OrderCard>
          ))}
        </OrdersList>

        {orders.length === 0 && (
          <EmptyState
            icon="receipt_long"
            title="אין הזמנות עדיין"
            message="התחל לקנות כדי לראות כאן את ההיסטוריה שלך"
            action={<button onClick={() => navigate('/scan')}>עבור לסריקה</button>}
          />
        )}
      </Container>
    </Layout>
  );
}
