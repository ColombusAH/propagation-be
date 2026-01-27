import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { theme } from '@/styles/theme';
import { useNavigate } from 'react-router-dom';
import { useStore } from '@/store';
import { useTranslation } from '@/hooks/useTranslation';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 800px;
  margin: 0 auto;
  background: linear-gradient(180deg, ${theme.colors.gray[50]} 0%, ${theme.colors.gray[100]} 100%);
  min-height: calc(100vh - 64px);
  animation: ${theme.animations.fadeIn};
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
  background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryDark} 100%);
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.lg};
  border-right: 10px solid ${theme.colors.primaryDark};
  color: white;
  text-align: center;
  animation: ${theme.animations.slideUp};

  h1, p {
    color: white;
  }
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  margin: 0;
  line-height: 1.2;
`;

const Subtitle = styled.p`
  margin: ${theme.spacing.sm} 0 0 0;
  opacity: 0.9;
`;

const ScanSection = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  margin-bottom: ${theme.spacing.xl};
  box-shadow: ${theme.shadows.md};
  text-align: center;
`;

const ScanButton = styled.button`
  width: 100%;
  max-width: 320px;
  padding: ${theme.spacing.xl};
  background: ${theme.colors.primaryGradient};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.xl};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  cursor: pointer;
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  transition: all ${theme.transitions.base};
  box-shadow: ${theme.shadows.md};

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px ${theme.colors.primary}30;
  }

  &:active {
    transform: translateY(-2px);
  }

  .material-symbols-outlined {
    font-size: 32px;
  }
`;

const CartSection = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  box-shadow: ${theme.shadows.lg};
  animation: ${theme.animations.slideUp};
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    height: 4px;
    background: ${theme.colors.primaryGradient};
  }
`;

const CartTitle = styled.h2`
  font-size: ${theme.typography.fontSize['xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.xl} 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 2px solid ${theme.colors.gray[100]};
  padding-bottom: ${theme.spacing.md};

  .material-symbols-outlined {
    font-size: 28px;
    color: ${theme.colors.primary};
  }

  span.count {
    background: ${theme.colors.primaryLight}20;
    color: ${theme.colors.primary};
    padding: 2px 12px;
    border-radius: ${theme.borderRadius.full};
    font-size: ${theme.typography.fontSize.sm};
  }
`;

const CartItemElement = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  padding: ${theme.spacing.lg};
  background: ${theme.colors.gray[50]};
  border: 1px solid ${theme.colors.borderLight};
  border-radius: ${theme.borderRadius.xl};
  margin-bottom: ${theme.spacing.md};
  transition: all ${theme.transitions.base};

  &:hover {
    background: white;
    border-color: ${theme.colors.primary};
    transform: translateX(-4px);
    box-shadow: ${theme.shadows.md};
  }
`;

const ItemIcon = styled.div`
  width: 48px;
  height: 48px;
  background: white;
  border-radius: ${theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${theme.colors.primary};
  box-shadow: ${theme.shadows.sm};

  .material-symbols-outlined {
    font-size: 28px;
  }
`;

const ItemInfo = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
`;

const ItemName = styled.span`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ItemMeta = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textMuted};
  display: flex;
  align-items: center;
  gap: 4px;
`;

const PriceWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
`;

const ItemPrice = styled.span`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
  white-space: nowrap;
`;

const RemoveButton = styled.button`
  width: 32px;
  height: 32px;
  color: ${theme.colors.error};
  background: white;
  border: 1px solid ${theme.colors.error}20;
  border-radius: ${theme.borderRadius.full};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all ${theme.transitions.fast};
  cursor: pointer;

  &:hover {
    background: ${theme.colors.error};
    color: white;
    transform: rotate(90deg);
  }

  .material-symbols-outlined {
    font-size: 18px;
  }
`;

const TotalSection = styled.div`
  margin-top: ${theme.spacing.xl};
  padding: ${theme.spacing.xl};
  background: ${theme.colors.gray[50]};
  border-radius: ${theme.borderRadius.xl};
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px dashed ${theme.colors.primary}40;
`;

const TotalLabel = styled.span`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.textLight};
`;

const TotalAmount = styled.span`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
  display: flex;
  align-items: baseline;
  gap: 4px;
`;

const PayButton = styled.button`
  width: 100%;
  margin-top: ${theme.spacing.xl};
  padding: ${theme.spacing.xl};
  background: linear-gradient(135deg, ${theme.colors.success} 0%, ${theme.colors.successDark} 100%);
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.xl};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  transition: all ${theme.transitions.base};
  box-shadow: 0 10px 20px ${theme.colors.success}30;

  &:hover:not(:disabled) {
    transform: translateY(-4px);
    box-shadow: 0 15px 30px ${theme.colors.success}50;
    filter: brightness(1.1);
  }

  &:active {
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .material-symbols-outlined {
    font-size: 32px;
  }
`;

const EmptyCart = styled.div`
  text-align: center;
  padding: ${theme.spacing['3xl']};
  color: ${theme.colors.textMuted};

  .material-symbols-outlined {
    font-size: 80px;
    color: ${theme.colors.primary}40;
    margin-bottom: ${theme.spacing.md};
  }

  p {
    margin: ${theme.spacing.sm} 0;
  }
`;

export function CustomerCartPage() {
  const navigate = useNavigate();
  const { items, getProductById, remove, getTotalInCents } = useStore();
  const { formatPrice } = useTranslation();

  const cartProducts = items.map(item => ({
    ...item,
    product: getProductById(item.productId)
  })).filter(item => item.product !== undefined);

  const totalInCents = getTotalInCents();

  const handlePayment = () => {
    navigate('/checkout');
  };

  return (
    <Layout>
      <Container>
        <Header>
          <Title>עגלת קניות</Title>
          <Subtitle>מוצרים שנוספו לעגלה</Subtitle>
        </Header>

        <ScanSection>
          <ScanButton onClick={() => navigate('/scan')}>
            <span className="material-symbols-outlined">qr_code_scanner</span>
            סרוק מוצר נוסף
          </ScanButton>
          <p style={{ marginTop: theme.spacing.md, color: theme.colors.textMuted, fontSize: theme.typography.fontSize.sm }}>
            סרוק את קוד ה-QR על התג או את הברקוד
          </p>
        </ScanSection>

        <CartSection>
          <CartTitle>
            <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
              <span className="material-symbols-outlined">shopping_cart</span>
              המוצרים שלך
            </div>
            <span className="count">{cartProducts.length}</span>
          </CartTitle>

          {cartProducts.length === 0 ? (
            <EmptyCart>
              <span className="material-symbols-outlined">shopping_basket</span>
              <p style={{ fontSize: theme.typography.fontSize.lg, fontWeight: 600 }}>העגלה ריקה</p>
              <p>הוסף מוצרים מהקטלוג או סרוק אותם כדי להתחיל</p>
            </EmptyCart>
          ) : (
            <>
              {cartProducts.map(({ product, productId, qty }) => (
                <CartItemElement key={productId}>
                  <ItemIcon>
                    <span className="material-symbols-outlined">inventory_2</span>
                  </ItemIcon>
                  <ItemInfo>
                    <ItemName>{product?.name}</ItemName>
                    <ItemMeta>
                      <span className="material-symbols-outlined" style={{ fontSize: 16 }}>layers</span>
                      כמות: {qty}
                    </ItemMeta>
                  </ItemInfo>
                  <PriceWrapper>
                    <ItemPrice>{formatPrice(product?.priceInCents || 0)}</ItemPrice>
                    <RemoveButton onClick={() => remove(productId)} title="הסר פריט">
                      <span className="material-symbols-outlined">close</span>
                    </RemoveButton>
                  </PriceWrapper>
                </CartItemElement>
              ))}

              <TotalSection>
                <TotalLabel>סה"כ לתשלום:</TotalLabel>
                <TotalAmount>{formatPrice(totalInCents)}</TotalAmount>
              </TotalSection>

              <PayButton
                onClick={handlePayment}
              >
                <span className="material-symbols-outlined">
                  credit_card
                </span>
                לתשלום
              </PayButton>
            </>
          )}
        </CartSection>
      </Container>
    </Layout>
  );
}
