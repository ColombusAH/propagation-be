import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { QuantityInput } from '@/components/QuantityInput';
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
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-bottom: 1px solid ${theme.colors.border};

  &:last-child {
    border-bottom: none;
  }

  &:nth-child(even) {
    background: ${theme.colors.backgroundAlt};
  }

  @media (max-width: ${theme.breakpoints.mobile}) {
    flex-wrap: wrap;
    padding: ${theme.spacing.md};
  }
`;

const ItemInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const ItemName = styled.h3`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.xs} 0;
`;

const ItemPrice = styled.p`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  margin: 0;
`;

const ItemSubtotal = styled.p`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  min-width: 80px;
  text-align: left;
  margin: 0;

  @media (max-width: ${theme.breakpoints.mobile}) {
    width: 100%;
    text-align: right;
  }
`;

const RemoveButton = styled.button`
  color: ${theme.colors.textMuted};
  background: none;
  border: none;
  cursor: pointer;
  padding: ${theme.spacing.xs};
  line-height: 1;
  transition: all ${theme.transitions.fast};
  border-radius: ${theme.borderRadius.sm};

  &:hover {
    color: ${theme.colors.error};
    background: ${theme.colors.surfaceHover};
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
    border-top: 1px solid ${theme.colors.border};
  }
`;

const SummaryLabel = styled.span`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const SummaryValue = styled.span`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
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
    props.variant === 'secondary' ? 'transparent' : theme.colors.primary};
  color: ${(props) =>
    props.variant === 'secondary' ? theme.colors.textSecondary : theme.colors.textInverse};
  border: ${(props) =>
    props.variant === 'secondary' ? `1px solid ${theme.colors.border}` : 'none'};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};
  box-shadow: ${(props) => (props.variant === 'secondary' ? 'none' : theme.shadows.sm)};

  &:hover {
    background-color: ${(props) =>
    props.variant === 'secondary' ? theme.colors.surfaceHover : theme.colors.primaryDark};
    border-color: ${(props) =>
    props.variant === 'secondary' ? theme.colors.borderDark : 'none'};
    box-shadow: ${(props) => (props.variant === 'secondary' ? 'none' : theme.shadows.md)};
  }
`;

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

export function CartPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
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
            icon="shopping_cart"
            title={t('cart.empty')}
            message={t('cart.emptyMessage')}
            action={
              <Button onClick={() => navigate('/scan')}>
                <MaterialIcon name="qr_code_scanner" /> {t('scan.title')}
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
          <MaterialIcon name="shopping_cart" size={24} />
          <Title>{t('cart.title')}</Title>
        </TitleRow>

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
                aria-label="הסר פריט"
              >
                <MaterialIcon name="close" size={20} />
              </RemoveButton>
            </CartItem>
          ))}
        </CartItems>

        <Summary>
          <SummaryRow>
            <SummaryLabel>{t('cart.total')}</SummaryLabel>
            <SummaryValue>{formatCurrency(total)}</SummaryValue>
          </SummaryRow>
          <Actions>
            <Button variant="secondary" onClick={clear}>
              <MaterialIcon name="delete_outline" /> {t('cart.remove')}
            </Button>
            <Button onClick={() => navigate('/checkout')}>
              <MaterialIcon name="payment" /> {t('cart.checkout')}
            </Button>
          </Actions>
        </Summary>
      </Container>
    </Layout>
  );
}
