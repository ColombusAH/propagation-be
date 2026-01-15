import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { formatCurrency } from '@/lib/utils/currency';
import { paySimple } from '@/payment/SimplePaymentProvider';
import { theme } from '@/styles/theme';

const Container = styled.div`
  max-width: 600px;
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

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
`;

const Label = styled.label`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.textSecondary};
`;

const Input = styled.input<{ hasError?: boolean }>`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${(props) => (props.hasError ? theme.colors.error : theme.colors.border)};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.sm};
  background: ${theme.colors.backgroundAlt};
  color: ${theme.colors.text};
  transition: all ${theme.transitions.fast};

  &::placeholder {
    color: ${theme.colors.textMuted};
  }

  &:focus {
    outline: none;
    border-color: ${(props) => (props.hasError ? theme.colors.error : theme.colors.borderFocus)};
    background: ${theme.colors.surface};
  }
`;

const Textarea = styled.textarea`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.sm};
  min-height: 80px;
  resize: vertical;
  font-family: inherit;
  background: ${theme.colors.backgroundAlt};
  color: ${theme.colors.text};
  transition: all ${theme.transitions.fast};

  &::placeholder {
    color: ${theme.colors.textMuted};
  }

  &:focus {
    outline: none;
    border-color: ${theme.colors.borderFocus};
    background: ${theme.colors.surface};
  }
`;

const ErrorMessage = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.error};
`;

const OrderSummary = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const OrderItem = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  padding: ${theme.spacing.xs} 0;
`;

const OrderTotal = styled.div`
  display: flex;
  justify-content: space-between;
  padding-top: ${theme.spacing.md};
  border-top: 1px solid ${theme.colors.border};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
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

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Actions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

export function CheckoutPage() {
  const navigate = useNavigate();
  const { items, getProductById, getTotalInCents, clear } = useStore();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    note: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isProcessing, setIsProcessing] = useState(false);

  const cartItems = items.map((item) => ({
    ...item,
    product: getProductById(item.productId)!,
  }));

  const total = getTotalInCents();

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'שם מלא הוא שדה חובה';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'אימייל הוא שדה חובה';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'אנא הזן כתובת אימייל תקינה';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsProcessing(true);

    try {
      const orderItems = items.map(item => ({
        productId: item.productId,
        qty: item.qty,
        priceInCents: getProductById(item.productId)?.priceInCents || 0
      }));
      
      const customer = {
        name: formData.name,
        email: formData.email,
        note: formData.note || undefined,
      };

      const result = await paySimple(orderItems, customer, total);

      if (result.ok) {
        clear();
        navigate(`/orders/${result.orderId}/success`);
      } else {
        setErrors({ submit: 'התשלום נכשל, אנא נסה שוב' });
      }
    } catch {
      setErrors({ submit: 'שגיאת תשלום, אנא נסה שוב' });
    } finally {
      setIsProcessing(false);
    }
  };

  if (items.length === 0) {
    return (
      <Layout>
        <Container>
          <EmptyState
            icon="shopping_cart"
            title="העגלה ריקה"
            message="הוסף מוצרים לעגלה כדי להמשיך לתשלום."
            action={
              <Button onClick={() => navigate('/scan')}>
                <MaterialIcon name="qr_code_scanner" /> סרוק מוצרים
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
          <MaterialIcon name="payment" size={24} />
          <Title>תשלום</Title>
        </TitleRow>

        <Form onSubmit={handleSubmit}>
          <Section>
            <SectionTitle>
              <MaterialIcon name="person" /> פרטי לקוח
            </SectionTitle>

            <FormGroup>
              <Label>שם מלא *</Label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                hasError={!!errors.name}
                placeholder="הזן שם מלא"
              />
              {errors.name && <ErrorMessage>{errors.name}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label>אימייל *</Label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                hasError={!!errors.email}
                placeholder="example@email.com"
              />
              {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label>הערות (אופציונלי)</Label>
              <Textarea
                value={formData.note}
                onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                placeholder="הוסף הערות להזמנה..."
              />
            </FormGroup>
          </Section>

          <Section>
            <SectionTitle>
              <MaterialIcon name="receipt" /> סיכום הזמנה
            </SectionTitle>

            <OrderSummary>
              {cartItems.map(({ product, qty }) => (
                <OrderItem key={product.id}>
                  <span>{product.name} × {qty}</span>
                  <span>{formatCurrency(product.priceInCents * qty)}</span>
                </OrderItem>
              ))}

              <OrderTotal>
                <span>סה"כ לתשלום</span>
                <span>{formatCurrency(total)}</span>
              </OrderTotal>
            </OrderSummary>
          </Section>

          {errors.submit && (
            <ErrorMessage style={{ textAlign: 'center', display: 'block' }}>
              {errors.submit}
            </ErrorMessage>
          )}

          <Actions>
            <Button type="submit" disabled={isProcessing}>
              <MaterialIcon name="lock" />
              {isProcessing ? 'מעבד...' : `שלם ${formatCurrency(total)}`}
            </Button>
            <Button type="button" variant="secondary" onClick={() => navigate('/cart')}>
              <MaterialIcon name="arrow_back" /> חזור לעגלה
            </Button>
          </Actions>
        </Form>
      </Container>
    </Layout>
  );
}
