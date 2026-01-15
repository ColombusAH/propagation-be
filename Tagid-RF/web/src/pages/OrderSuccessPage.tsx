import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { formatCurrency } from '@/lib/utils/currency';
import { theme } from '@/styles/theme';

const Container = styled.div`
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
`;

const SuccessHeader = styled.div`
  text-align: center;
  margin-bottom: ${theme.spacing.xl};
`;

const SuccessIcon = styled.div`
  width: 80px;
  height: 80px;
  margin: 0 auto ${theme.spacing.lg};
  background: ${theme.colors.success};
  border-radius: ${theme.borderRadius.full};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${theme.colors.text};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Subtitle = styled.p`
  color: ${theme.colors.textSecondary};
  margin: 0;
  font-size: ${theme.typography.fontSize.base};
`;

const Section = styled.section`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};
  margin: 0 0 ${theme.spacing.md} 0;
  color: ${theme.colors.text};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: ${theme.spacing.sm} 0;
  font-size: ${theme.typography.fontSize.sm};
  border-bottom: 1px solid ${theme.colors.border};

  &:last-child {
    border-bottom: none;
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
  color: ${theme.colors.textSecondary};

  &:last-child {
    border-bottom: none;
  }
`;

const TotalRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding-top: ${theme.spacing.md};
  margin-top: ${theme.spacing.md};
  border-top: 1px solid ${theme.colors.border};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
`;

const Actions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  background-color: ${(props) =>
    props.variant === 'secondary' ? 'transparent' : theme.colors.primary};
  color: ${(props) =>
    props.variant === 'secondary' ? theme.colors.primary : theme.colors.textInverse};
  border: 1px solid ${(props) =>
    props.variant === 'secondary' ? theme.colors.border : theme.colors.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};

  &:hover {
    background-color: ${(props) =>
      props.variant === 'secondary' ? theme.colors.surfaceHover : theme.colors.primaryDark};
    border-color: ${(props) =>
      props.variant === 'secondary' ? theme.colors.borderDark : theme.colors.primaryDark};
  }
`;

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

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
            icon="help_outline"
            title="הזמנה לא נמצאה"
            message="ההזמנה שאתה מחפש לא קיימת."
            action={
              <Button onClick={() => navigate('/scan')}>
                <MaterialIcon name="add_shopping_cart" /> התחל רכישה חדשה
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
        <SuccessHeader>
          <SuccessIcon>
            <MaterialIcon name="check" size={40} />
          </SuccessIcon>
          <Title>התשלום הצליח!</Title>
          <Subtitle>ההזמנה שלך הושלמה בהצלחה.</Subtitle>
        </SuccessHeader>

        <Section>
          <SectionTitle>
            <MaterialIcon name="receipt" /> פרטי הזמנה
          </SectionTitle>
          <InfoRow>
            <Label>מספר הזמנה</Label>
            <Value style={{ fontFamily: theme.typography.fontFamily.mono }}>
              #{order.id.slice(0, 8)}
            </Value>
          </InfoRow>
          <InfoRow>
            <Label>תאריך</Label>
            <Value>{orderDate.toLocaleString('he-IL')}</Value>
          </InfoRow>
          <InfoRow>
            <Label>סטטוס</Label>
            <Value style={{ color: theme.colors.success }}>
              {order.status === 'PAID' ? 'שולם' : order.status}
            </Value>
          </InfoRow>
        </Section>

        <Section>
          <SectionTitle>
            <MaterialIcon name="person" /> פרטי לקוח
          </SectionTitle>
          <InfoRow>
            <Label>שם</Label>
            <Value>{order.customer.name}</Value>
          </InfoRow>
          <InfoRow>
            <Label>אימייל</Label>
            <Value>{order.customer.email}</Value>
          </InfoRow>
          {order.customer.note && (
            <InfoRow>
              <Label>הערות</Label>
              <Value>{order.customer.note}</Value>
            </InfoRow>
          )}
        </Section>

        <Section>
          <SectionTitle>
            <MaterialIcon name="inventory_2" /> פריטים
          </SectionTitle>
          <OrderItems>
            {order.items.map((item) => {
              const product = getProductById(item.productId);
              return (
                <OrderItem key={item.productId}>
                  <span>{product?.name || 'מוצר'} × {item.qty}</span>
                  <span>{formatCurrency(item.priceInCents * item.qty)}</span>
                </OrderItem>
              );
            })}
          </OrderItems>
          <TotalRow>
            <span>סה"כ</span>
            <span>{formatCurrency(order.totalInCents)}</span>
          </TotalRow>
        </Section>

        <Actions>
          <Button onClick={() => navigate('/scan')}>
            <MaterialIcon name="add_shopping_cart" /> התחל רכישה חדשה
          </Button>
          <Button variant="secondary" onClick={() => navigate('/orders')}>
            <MaterialIcon name="list" /> כל ההזמנות
          </Button>
        </Actions>
      </Container>
    </Layout>
  );
}
