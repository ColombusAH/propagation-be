import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { useTranslation } from '@/hooks/useTranslation';
import { formatCurrency } from '@/lib/utils/currency';
import { theme } from '@/styles/theme';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
`;

const TitleRow = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
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
    border-color: ${theme.colors.borderDark};
    box-shadow: ${theme.shadows.md};
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
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textMuted};
  margin-bottom: ${theme.spacing.xs};
  font-family: ${theme.typography.fontFamily.mono};
`;

const OrderDate = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const OrderTotal = styled.div`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  text-align: left;

  @media (max-width: ${theme.breakpoints.mobile}) {
    text-align: right;
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
  display: inline-flex;
  align-items: center;
  gap: ${theme.spacing.xs};
  background-color: ${theme.colors.success};
  color: ${theme.colors.text};
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.medium};
  margin-top: ${theme.spacing.sm};
`;

const Button = styled.button`
  background-color: ${theme.colors.primary};
  color: ${theme.colors.textInverse};
  border: 1px solid ${theme.colors.primary};
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
    background-color: ${theme.colors.primaryDark};
    border-color: ${theme.colors.primaryDark};
  }
`;

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

export function OrdersPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { list, getProductById } = useStore();
  const orders = list();

  if (orders.length === 0) {
    return (
      <Layout>
        <Container>
          <EmptyState
            icon="receipt_long"
            title={t('orders.empty')}
            message={t('orders.emptyMessage')}
            action={
              <Button onClick={() => navigate('/scan')}>
                <MaterialIcon name="qr_code_scanner" /> {t('cart.continueShopping')}
              </Button>
            }
          />
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container>
        <TitleRow>
          <MaterialIcon name="receipt_long" size={24} />
          <Title>{t('orders.title')}</Title>
        </TitleRow>

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
                    <OrderId>{t('orders.orderNumber')} #{order.id.slice(0, 8)}</OrderId>
                    <OrderDate>{orderDate.toLocaleString('he-IL')}</OrderDate>
                    <Status>
                      <MaterialIcon name="check_circle" size={14} />
                      {t('orders.paid')}
                    </Status>
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
                        {product?.name || 'מוצר'} × {item.qty}
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
