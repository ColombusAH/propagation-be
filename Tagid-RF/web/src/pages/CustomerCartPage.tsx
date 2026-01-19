import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { theme } from '@/styles/theme';

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
  max-width: 300px;
  padding: ${theme.spacing.xl};
  background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryDark} 100%);
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.xl};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  cursor: pointer;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  transition: all ${theme.transitions.base};
  box-shadow: ${theme.shadows.lg};

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px ${theme.colors.primary}40;
  }

  &:active {
    transform: translateY(-2px);
  }

  .material-symbols-outlined {
    font-size: 48px;
  }
`;

const CartSection = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  box-shadow: ${theme.shadows.md};
  animation: ${theme.animations.slideUp};
`;

const CartTitle = styled.h2`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.lg} 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};

  .material-symbols-outlined {
    font-size: 28px;
    color: ${theme.colors.primary};
  }
`;

const CartItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  margin-bottom: ${theme.spacing.sm};
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.gray[50]};
  }
`;

const ItemInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ItemName = styled.span`
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
`;

const ItemMeta = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textMuted};
`;

const ItemPrice = styled.span`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
`;

const RemoveButton = styled.button`
  padding: ${theme.spacing.xs};
  color: ${theme.colors.error};
  border-radius: ${theme.borderRadius.sm};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.errorLight};
  }

  .material-symbols-outlined {
    font-size: 20px;
  }
`;

const TotalSection = styled.div`
  margin-top: ${theme.spacing.xl};
  padding-top: ${theme.spacing.xl};
  border-top: 2px solid ${theme.colors.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const TotalLabel = styled.span`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
`;

const TotalAmount = styled.span`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
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
  box-shadow: ${theme.shadows.lg};

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px ${theme.colors.success}40;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  .material-symbols-outlined {
    font-size: 28px;
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

const SuccessOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${theme.colors.success}F2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  color: white;
  animation: ${theme.animations.fadeIn};

  .material-symbols-outlined {
    font-size: 120px;
    margin-bottom: ${theme.spacing.xl};
  }

  h1 {
    font-size: ${theme.typography.fontSize['4xl']};
    margin: 0 0 ${theme.spacing.md} 0;
  }

  p {
    font-size: ${theme.typography.fontSize.xl};
    opacity: 0.9;
  }
`;

interface CartProduct {
    id: string;
    epc: string;
    name: string;
    price: number;
    category: string;
}

export function CustomerCartPage() {
    const [cartItems, setCartItems] = useState<CartProduct[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);

    const simulateScan = () => {
        const products = [
            { name: 'חולצת טי כחולה', price: 89.90, category: 'ביגוד' },
            { name: 'מכנסי ג\'ינס', price: 199.90, category: 'ביגוד' },
            { name: 'נעלי ספורט', price: 349.90, category: 'הנעלה' },
            { name: 'שעון יד', price: 299.90, category: 'אביזרים' },
            { name: 'תיק גב', price: 149.90, category: 'אביזרים' },
        ];

        const randomProduct = products[Math.floor(Math.random() * products.length)];
        const newItem: CartProduct = {
            id: crypto.randomUUID(),
            epc: `E2${Math.random().toString(16).substring(2, 18).toUpperCase()}`,
            name: randomProduct.name,
            price: randomProduct.price,
            category: randomProduct.category,
        };

        if (!cartItems.find(item => item.epc === newItem.epc)) {
            setCartItems(prev => [...prev, newItem]);
        }
    };

    const removeItem = (id: string) => {
        setCartItems(prev => prev.filter(item => item.id !== id));
    };

    const totalAmount = cartItems.reduce((sum, item) => sum + item.price, 0);

    const handlePayment = () => {
        setIsProcessing(true);

        setTimeout(() => {
            setIsProcessing(false);
            setShowSuccess(true);
            setCartItems([]);

            setTimeout(() => {
                setShowSuccess(false);
            }, 3000);
        }, 2000);
    };

    if (showSuccess) {
        return (
            <SuccessOverlay>
                <span className="material-symbols-outlined">check_circle</span>
                <h1>התשלום הושלם!</h1>
                <p>תודה על הקנייה</p>
            </SuccessOverlay>
        );
    }

    return (
        <Layout>
            <Container>
                <Header>
                    <Title>עגלת קניות</Title>
                    <Subtitle>סרוק מוצרים והוסף לעגלה</Subtitle>
                </Header>

                <ScanSection>
                    <ScanButton onClick={simulateScan}>
                        <span className="material-symbols-outlined">qr_code_scanner</span>
                        סרוק מוצר
                    </ScanButton>
                    <p style={{ marginTop: theme.spacing.md, color: theme.colors.textMuted, fontSize: theme.typography.fontSize.sm }}>
                        סרוק את קוד ה-QR על התג או הנח מוצרים באמבט
                    </p>
                </ScanSection>

                <CartSection>
                    <CartTitle>
                        <span className="material-symbols-outlined">shopping_cart</span>
                        המוצרים שלך ({cartItems.length})
                    </CartTitle>

                    {cartItems.length === 0 ? (
                        <EmptyCart>
                            <span className="material-symbols-outlined">shopping_cart</span>
                            <p style={{ fontSize: theme.typography.fontSize.lg, fontWeight: 500 }}>העגלה ריקה</p>
                            <p>סרוק מוצרים כדי להוסיף לעגלה</p>
                        </EmptyCart>
                    ) : (
                        <>
                            {cartItems.map(item => (
                                <CartItem key={item.id}>
                                    <ItemInfo>
                                        <ItemName>{item.name}</ItemName>
                                        <ItemMeta>{item.category}</ItemMeta>
                                    </ItemInfo>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md }}>
                                        <ItemPrice>{item.price.toFixed(2)} ש"ח</ItemPrice>
                                        <RemoveButton onClick={() => removeItem(item.id)}>
                                            <span className="material-symbols-outlined">close</span>
                                        </RemoveButton>
                                    </div>
                                </CartItem>
                            ))}

                            <TotalSection>
                                <TotalLabel>סה"כ לתשלום:</TotalLabel>
                                <TotalAmount>{totalAmount.toFixed(2)} ש"ח</TotalAmount>
                            </TotalSection>

                            <PayButton
                                onClick={handlePayment}
                                disabled={isProcessing}
                            >
                                <span className="material-symbols-outlined">
                                    {isProcessing ? 'autorenew' : 'credit_card'}
                                </span>
                                {isProcessing ? 'מעבד תשלום...' : 'לתשלום'}
                            </PayButton>
                        </>
                    )}
                </CartSection>
            </Container>
        </Layout>
    );
}
