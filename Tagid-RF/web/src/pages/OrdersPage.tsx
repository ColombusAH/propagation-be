import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { formatCurrency } from '@/lib/utils/currency';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
`;

const Title = styled.h1`
  margin-bottom: ${theme.spacing.lg};
`;

const OrdersList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const OrderCard = styled.div`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    box-shadow: ${theme.shadows.md};
    border-color: ${theme.colors.primary};
  }
`;

const OrderHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: ${theme.spacing.md};
  gap: ${theme.spacing.md};

  @media (max-width: ${theme.breakpoints.mobile}) {
    flex-direction: column;
  }
`;

const OrderInfo = styled.div`
  flex: 1;
`;

const OrderId = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.xs};
`;

const OrderDate = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const OrderTotal = styled.div`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
  text-align: right;

  @media (max-width: ${theme.breakpoints.mobile}) {
    text-align: left;
  }
`;

const OrderItems = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
`;

const OrderItem = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const Status = styled.span`
  display: inline-block;
  background-color: ${theme.colors.success};
  color: white;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.medium};
  margin-top: ${theme.spacing.sm};
`;

const Button = styled.button`
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.base};
  cursor: pointer;
  transition: background-color ${theme.transitions.fast};

  &:hover {
    background-color: ${theme.colors.primaryDark};
  }
`;

export function OrdersPage() {
  const navigate = useNavigate();
  const { list, getProductById } = useStore();
  const orders = list();

  if (orders.length === 0) {
    return (
      <Layout>
        <Container>
          <EmptyState
            icon="📋"
            title="No orders yet"
            message="You haven't placed any orders yet. Start shopping to see your orders here."
            action={
              <Button onClick={() => navigate('/scan')}>Start Shopping</Button>
            }
          />
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container>
        <Title>📋 Order History</Title>

        <OrdersList>
          {orders.map((order) => {
            const orderDate = new Date(order.createdAt);
            return (
              <OrderCard
                key={order.id}
                onClick={() => navigate(`/orders/${order.id}/success`)}
              >
                <OrderHeader>
                  <OrderInfo>
                    <OrderId>Order #{order.id.slice(0, 8)}</OrderId>
                    <OrderDate>{orderDate.toLocaleString()}</OrderDate>
                    <Status>{order.status}</Status>
                  </OrderInfo>
                  <OrderTotal>
                    {formatCurrency(order.totalInCents)}
                  </OrderTotal>
                </OrderHeader>

                <OrderItems>
                  {order.items.map((item) => {
                    const product = getProductById(item.productId);
                    return (
                      <OrderItem key={item.productId}>
                        {product?.name || 'Unknown'} × {item.qty}
                      </OrderItem>
                    );
                  })}
                </OrderItems>
              </OrderCard>
            );
          })}
        </OrdersList>
      </Container>
    </Layout>
  );
}

