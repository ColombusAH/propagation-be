import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { formatCurrency } from '@/lib/utils/currency';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
`;

const SuccessIcon = styled.div`
  font-size: 80px;
  text-align: center;
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  text-align: center;
  color: ${theme.colors.success};
  margin-bottom: ${theme.spacing.md};
`;

const Subtitle = styled.p`
  text-align: center;
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.xl};
`;

const Section = styled.section`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  font-size: ${theme.typography.fontSize.lg};
  margin-bottom: ${theme.spacing.md};
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: ${theme.spacing.sm} 0;
  font-size: ${theme.typography.fontSize.sm};

  &:not(:last-child) {
    border-bottom: 1px solid ${theme.colors.border};
  }
`;

const Label = styled.span`
  color: ${theme.colors.textSecondary};
`;

const Value = styled.span`
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const OrderItems = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const OrderItem = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: ${theme.typography.fontSize.sm};
  padding: ${theme.spacing.sm} 0;
  border-bottom: 1px solid ${theme.colors.border};

  &:last-child {
    border-bottom: none;
  }
`;

const TotalRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding-top: ${theme.spacing.md};
  margin-top: ${theme.spacing.md};
  border-top: 2px solid ${theme.colors.border};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
`;

const Actions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  background-color: ${(props) =>
    props.variant === 'secondary'
      ? theme.colors.backgroundAlt
      : theme.colors.primary};
  color: ${(props) =>
    props.variant === 'secondary' ? theme.colors.text : 'white'};
  border: 1px solid
    ${(props) =>
      props.variant === 'secondary'
        ? theme.colors.border
        : theme.colors.primary};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.base};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    background-color: ${(props) =>
      props.variant === 'secondary'
        ? theme.colors.border
        : theme.colors.primaryDark};
  }
`;

export function OrderSuccessPage() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { getById, getProductById } = useStore();

  const order = orderId ? getById(orderId) : undefined;

  if (!order) {
    return (
      <Layout>
        <Container>
          <EmptyState
            icon="❓"
            title="Order not found"
            message="The order you're looking for doesn't exist."
            action={
              <Button onClick={() => navigate('/scan')}>
                Start New Purchase
              </Button>
            }
          />
        </Container>
      </Layout>
    );
  }

  const orderDate = new Date(order.createdAt);

  return (
    <Layout>
      <Container>
        <SuccessIcon>✓</SuccessIcon>
        <Title>Payment Successful!</Title>
        <Subtitle>Your order has been placed successfully.</Subtitle>

        <Section>
          <SectionTitle>Order Details</SectionTitle>
          <InfoRow>
            <Label>Order ID</Label>
            <Value>{order.id.slice(0, 8)}...</Value>
          </InfoRow>
          <InfoRow>
            <Label>Date</Label>
            <Value>{orderDate.toLocaleString()}</Value>
          </InfoRow>
          <InfoRow>
            <Label>Status</Label>
            <Value>{order.status}</Value>
          </InfoRow>
        </Section>

        <Section>
          <SectionTitle>Customer Information</SectionTitle>
          <InfoRow>
            <Label>Name</Label>
            <Value>{order.customer.name}</Value>
          </InfoRow>
          <InfoRow>
            <Label>Email</Label>
            <Value>{order.customer.email}</Value>
          </InfoRow>
          {order.customer.note && (
            <InfoRow>
              <Label>Note</Label>
              <Value>{order.customer.note}</Value>
            </InfoRow>
          )}
        </Section>

        <Section>
          <SectionTitle>Items</SectionTitle>
          <OrderItems>
            {order.items.map((item) => {
              const product = getProductById(item.productId);
              return (
                <OrderItem key={item.productId}>
                  <span>
                    {product?.name || 'Unknown'} × {item.qty}
                  </span>
                  <span>
                    {formatCurrency(item.priceInCents * item.qty)}
                  </span>
                </OrderItem>
              );
            })}
          </OrderItems>
          <TotalRow>
            <span>Total</span>
            <span>{formatCurrency(order.totalInCents)}</span>
          </TotalRow>
        </Section>

        <Actions>
          <Button onClick={() => navigate('/scan')}>
            Start New Purchase
          </Button>
          <Button variant="secondary" onClick={() => navigate('/orders')}>
            View All Orders
          </Button>
        </Actions>
      </Container>
    </Layout>
  );
}

