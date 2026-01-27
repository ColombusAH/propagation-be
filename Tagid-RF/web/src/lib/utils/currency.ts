import { MoneyCents } from '@/store/types';

export function formatCurrency(
  cents: MoneyCents,
  locale = 'he-IL',
  currency = 'ILS'
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

