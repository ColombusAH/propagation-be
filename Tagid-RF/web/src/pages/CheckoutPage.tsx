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
  padding: ${theme.spacing.lg};
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
`;

const Title = styled.h1`
  margin-bottom: ${theme.spacing.lg};
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
  color: ${theme.colors.text};
`;

const Input = styled.input<{ hasError?: boolean }>`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid
    ${(props) => (props.hasError ? theme.colors.error : theme.colors.border)};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};

  &:focus {
    outline: none;
    border-color: ${(props) =>
      props.hasError ? theme.colors.error : theme.colors.primary};
  }
`;

const Textarea = styled.textarea`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  min-height: 80px;
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const ErrorMessage = styled.span`
  font-size: ${theme.typography.fontSize.sm};
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
`;

const OrderTotal = styled.div`
  display: flex;
  justify-content: space-between;
  padding-top: ${theme.spacing.md};
  border-top: 2px solid ${theme.colors.border};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
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
  width: 100%;

  &:hover:not(:disabled) {
    background-color: ${(props) =>
      props.variant === 'secondary'
        ? theme.colors.border
        : theme.colors.primaryDark};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
`;

export function CheckoutPage() {
  const navigate = useNavigate();
  const { items, getProductById, getTotalInCents, clear } = useStore();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [note, setNote] = useState('');
  const [errors, setErrors] = useState<{ name?: string; email?: string }>({});
  const [isProcessing, setIsProcessing] = useState(false);

  if (items.length === 0) {
    return (
      <Layout>
        <Container>
          <EmptyState
            icon="🛒"
            title="Your cart is empty"
            message="Add items to your cart before checking out."
            action={
              <Button onClick={() => navigate('/scan')}>Start Scanning</Button>
            }
          />
        </Container>
      </Layout>
    );
  }

  const cartItems = items.map((item) => ({
    ...item,
    product: getProductById(item.productId)!,
  }));

  const total = getTotalInCents();

  const validateForm = () => {
    const newErrors: { name?: string; email?: string } = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsProcessing(true);

    try {
      const orderItems = items.map((item) => ({
        productId: item.productId,
        qty: item.qty,
        priceInCents: getProductById(item.productId)!.priceInCents,
      }));

      const result = await paySimple(
        orderItems,
        { name, email, note: note || undefined },
        total
      );

      clear();
      navigate(`/orders/${result.orderId}/success`);
    } catch (error) {
      console.error('Payment failed:', error);
      alert('Payment failed. Please try again.');
      setIsProcessing(false);
    }
  };

  return (
    <Layout>
      <Container>
        <Title>💳 Checkout</Title>

        <Section>
          <SectionTitle>Order Summary</SectionTitle>
          <OrderSummary>
            {cartItems.map(({ product, productId, qty }) => (
              <OrderItem key={productId}>
                <span>
                  {product.name} × {qty}
                </span>
                <span>{formatCurrency(product.priceInCents * qty)}</span>
              </OrderItem>
            ))}
            <OrderTotal>
              <span>Total</span>
              <span>{formatCurrency(total)}</span>
            </OrderTotal>
          </OrderSummary>
        </Section>

        <Section>
          <SectionTitle>Customer Information</SectionTitle>
          <Form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                hasError={!!errors.name}
                placeholder="John Doe"
              />
              {errors.name && <ErrorMessage>{errors.name}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                hasError={!!errors.email}
                placeholder="john@example.com"
              />
              {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="note">Note (optional)</Label>
              <Textarea
                id="note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add any special instructions..."
              />
            </FormGroup>

            <ButtonGroup>
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/cart')}
                disabled={isProcessing}
              >
                Back to Cart
              </Button>
              <Button type="submit" disabled={isProcessing}>
                {isProcessing ? 'Processing...' : 'Pay Now'}
              </Button>
            </ButtonGroup>
          </Form>
        </Section>
      </Container>
    </Layout>
  );
}

