import { MoneyCents } from '@/store/types';

export function formatCurrency(
  cents: MoneyCents,
  locale = 'en-US',
  currency = 'USD'
): string {
  const amount = cents / 100;
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount);
}

export function parseCentsToDecimal(cents: MoneyCents): string {
  return (cents / 100).toFixed(2);
}

