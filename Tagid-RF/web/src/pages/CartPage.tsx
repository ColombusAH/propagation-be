import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { QuantityInput } from '@/components/QuantityInput';
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

const CartItems = styled.div`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  overflow: hidden;
  margin-bottom: ${theme.spacing.lg};
`;

const CartItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.border};

  &:last-child {
    border-bottom: none;
  }

  @media (max-width: ${theme.breakpoints.mobile}) {
    flex-wrap: wrap;
  }
`;

const ItemInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const ItemName = styled.h3`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};
  margin-bottom: ${theme.spacing.xs};
`;

const ItemPrice = styled.p`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const ItemSubtotal = styled.p`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.primary};
  min-width: 80px;
  text-align: right;

  @media (max-width: ${theme.breakpoints.mobile}) {
    width: 100%;
    text-align: left;
  }
`;

const RemoveButton = styled.button`
  color: ${theme.colors.danger};
  background: none;
  border: none;
  cursor: pointer;
  font-size: ${theme.typography.fontSize.xl};
  padding: ${theme.spacing.xs};
  line-height: 1;
  transition: opacity ${theme.transitions.fast};

  &:hover {
    opacity: 0.7;
  }
`;

const Summary = styled.div`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.md};

  &:last-child {
    margin-bottom: 0;
    padding-top: ${theme.spacing.md};
    border-top: 2px solid ${theme.colors.border};
  }
`;

const SummaryLabel = styled.span`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const SummaryValue = styled.span`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
`;

const Actions = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.lg};

  @media (max-width: ${theme.breakpoints.mobile}) {
    flex-direction: column;
  }
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  flex: 1;
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

export function CartPage() {
  const navigate = useNavigate();
  const { items, getProductById, setQty, remove, clear, getTotalInCents } =
    useStore();

  const cartItems = items.map((item) => ({
    ...item,
    product: getProductById(item.productId)!,
  }));

  const total = getTotalInCents();

  if (items.length === 0) {
    return (
      <Layout>
        <Container>
          <EmptyState
            icon="🛒"
            title="Your cart is empty"
            message="Scan products or browse the catalog to add items to your cart."
            action={
              <Button onClick={() => navigate('/scan')}>Start Scanning</Button>
            }
          />
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container>
        <Title>🛒 Shopping Cart</Title>

        <CartItems>
          {cartItems.map(({ product, productId, qty }) => (
            <CartItem key={productId}>
              <ItemInfo>
                <ItemName>{product.name}</ItemName>
                <ItemPrice>{formatCurrency(product.priceInCents)}</ItemPrice>
              </ItemInfo>
              <QuantityInput
                value={qty}
                onChange={(newQty) => setQty(productId, newQty)}
              />
              <ItemSubtotal>
                {formatCurrency(product.priceInCents * qty)}
              </ItemSubtotal>
              <RemoveButton
                onClick={() => remove(productId)}
                aria-label="Remove item"
              >
                ×
              </RemoveButton>
            </CartItem>
          ))}
        </CartItems>

        <Summary>
          <SummaryRow>
            <SummaryLabel>Total</SummaryLabel>
            <SummaryValue>{formatCurrency(total)}</SummaryValue>
          </SummaryRow>
          <Actions>
            <Button variant="secondary" onClick={clear}>
              Clear Cart
            </Button>
            <Button onClick={() => navigate('/checkout')}>
              Proceed to Checkout
            </Button>
          </Actions>
        </Summary>
      </Container>
    </Layout>
  );
}

