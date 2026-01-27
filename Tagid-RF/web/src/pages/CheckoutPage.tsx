import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import styled from 'styled-components';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';
import { Layout } from '@/components/Layout';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { formatCurrency } from '@/lib/utils/currency';
import { payWithStripe, confirmPayment } from '@/payment/StripePaymentProvider';
import { theme } from '@/styles/theme';
import { useToast } from '@/hooks/useToast';

// @ts-ignore
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');

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
  background: white;
  border: 1px solid ${theme.colors.borderLight};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  margin-bottom: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.md};
  transition: all ${theme.transitions.base};

  &:hover {
    box-shadow: ${theme.shadows.lg};
    border-color: ${theme.colors.primaryLight};
  }
`;

const SectionTitle = styled.h2`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  margin: 0 0 ${theme.spacing.lg} 0;
  color: ${theme.colors.text};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  border-bottom: 2px solid ${theme.colors.gray[50]};
  padding-bottom: ${theme.spacing.sm};

  .material-symbols-outlined {
    color: ${theme.colors.primary};
  }
`;

const CardElementContainer = styled.div`
  padding: ${theme.spacing.lg};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  background: ${theme.colors.gray[50]};
  margin: ${theme.spacing.md} 0;
  transition: all ${theme.transitions.fast};

  &:focus-within {
    border-color: ${theme.colors.primary};
    background: white;
    box-shadow: 0 0 0 4px ${theme.colors.primary}15;
  }
`;

const OrderSummary = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const OrderTotal = styled.div`
  display: flex;
  justify-content: space-between;
  padding: ${theme.spacing.md} 0;
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
`;

const Button = styled.button`
  width: 100%;
  background: ${theme.colors.primaryGradient};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  font-size: ${theme.typography.fontSize.lg};
  cursor: pointer;
  transition: all ${theme.transitions.base};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  box-shadow: 0 10px 20px ${theme.colors.primary}30;

  &:hover:not(:disabled) {
    transform: translateY(-4px);
    box-shadow: 0 15px 30px ${theme.colors.primary}50;
    filter: brightness(1.1);
  }

  &:active {
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

function StripeCheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();
  const { getTotalInCents, clear } = useStore();
  const { isAuthenticated } = useAuth();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const total = getTotalInCents();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (!stripe || !elements) return;

    setIsProcessing(true);
    setError(null);

    try {
      // 1. Create order and get payment intent from backend
      const result = await payWithStripe('REAL_ORDER_' + Date.now(), total);

      if (!result.ok || !result.clientSecret) {
        throw new Error(result.error || 'Failed to initialize payment');
      }

      const clientSecret = result.clientSecret as string;
      const paymentId = result.paymentId as string;

      // 2. Confirm payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(
        clientSecret,
        {
          payment_method: {
            card: elements.getElement(CardElement)!,
          },
        }
      );

      if (stripeError) {
        throw new Error(stripeError.message);
      }

      if (paymentIntent && paymentIntent.status === 'succeeded') {
        // Update payment status in our database
        await confirmPayment(paymentId);

        clear();
        toast.success('התשלום בוצע בהצלחה. תודה על הרכישה.');
        navigate(`/orders/${paymentId}/success`);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Section>
        <SectionTitle>
          <MaterialIcon name="credit_card" /> פרטי תשלום (Stripe)
        </SectionTitle>
        <CardElementContainer>
          <CardElement
            options={{
              hidePostalCode: true,
              style: {
                base: {
                  fontSize: '16px',
                  color: theme.colors.text,
                  '::placeholder': {
                    color: theme.colors.textMuted,
                  },
                },
              },
            }}
          />
        </CardElementContainer>
        {error && <div style={{ color: theme.colors.error, marginTop: '10px', fontSize: '14px' }}>{error}</div>}
      </Section>

      <Section>
        <SectionTitle>
          <MaterialIcon name="receipt" /> סיכום
        </SectionTitle>
        <OrderSummary>
          <OrderTotal>
            <span>סה"כ</span>
            <span>{formatCurrency(total)}</span>
          </OrderTotal>
        </OrderSummary>
      </Section>

      <Button type="submit" disabled={(isAuthenticated && !stripe) || isProcessing}>
        <MaterialIcon name={isProcessing ? 'sync' : (isAuthenticated ? 'payments' : 'login')} />
        {isProcessing ? 'מעבד תשלום...' : (isAuthenticated ? 'בצע תשלום' : 'התחבר כדי לשלם')}
      </Button>
    </form>
  );
}

export function CheckoutPage() {
  const { items } = useStore();
  const navigate = useNavigate();

  if (items.length === 0) {
    return (
      <Layout>
        <Container>
          <EmptyState
            icon="shopping_cart"
            title="העגלה ריקה"
            message="הוסף מוצרים לעגלה כדי להמשיך לתשלום."
            action={<Button onClick={() => navigate('/scan')}>חזור לסריקה</Button>}
          />
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container>
        <TitleRow>
          <MaterialIcon name="verified_user" size={32} />
          <Title>תשלום מאובטח</Title>
        </TitleRow>

        <Elements stripe={stripePromise}>
          <StripeCheckoutForm />
        </Elements>
      </Container>
    </Layout>
  );
}
