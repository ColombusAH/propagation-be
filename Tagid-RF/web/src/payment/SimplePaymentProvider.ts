import { v4 as uuidv4 } from '@/lib/utils/uuid';
import { Order } from '@/store/types';
import { useStore } from '@/store';
import { PaymentResult } from './types';

export async function paySimple(
  items: Array<{
    productId: string;
    qty: number;
    priceInCents: number;
  }>,
  customer: { name: string; email: string; note?: string },
  totalInCents: number
): Promise<PaymentResult> {
  // Simulate network latency
  await new Promise((resolve) => setTimeout(resolve, 600));

  // Generate order ID
  const orderId = uuidv4();

  // Create order object
  const order: Order = {
    id: orderId,
    items,
    totalInCents,
    customer,
    createdAt: new Date().toISOString(),
    status: 'PAID',
  };

  // Store order in Zustand
  useStore.getState().createOrder(order);

  return { ok: true, orderId };
}

