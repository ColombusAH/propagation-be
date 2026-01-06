// i18n barrel export
export { en, type TranslationKeys } from './en';
export { he } from './he';

export type Locale = 'en' | 'he';
export type Currency = 'ILS' | 'USD' | 'EUR';

export const currencySymbols: Record<Currency, string> = {
    ILS: '₪',
    USD: '$',
    EUR: '€',
};

export const currencyLocales: Record<Currency, string> = {
    ILS: 'he-IL',
    USD: 'en-US',
    EUR: 'de-DE',
};

export const isRTL = (locale: Locale): boolean => locale === 'he';
