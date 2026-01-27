import { MoneyCents } from '@/store/types';

export interface PaymentResult {
  ok: boolean;
  orderId: string;
  clientSecret?: string;
  paymentId?: string;
  error?: string;
}

export interface PaymentRequest {
  items: Array<{
    productId: string;
    qty: number;
    priceInCents: MoneyCents;
  }>;
  customer: {
    name: string;
    email: string;
    note?: string;
  };
  totalInCents: MoneyCents;
}
