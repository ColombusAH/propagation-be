import { useStore } from '@/store';
import { en, he, currencySymbols, currencyLocales, type TranslationKeys } from '@/i18n';

type NestedKeyOf<T> = T extends object
    ? { [K in keyof T]: K extends string ? (T[K] extends object ? `${K}.${NestedKeyOf<T[K]>}` : K) : never }[keyof T]
    : never;

// Exported for future type-safe translation keys
export type _TranslationPath = NestedKeyOf<TranslationKeys>;

const translations = { en, he };

/**
 * Get nested value from object using dot notation path
 */
function getNestedValue(obj: Record<string, unknown>, path: string): string {
    const keys = path.split('.');
    let result: unknown = obj;

    for (const key of keys) {
        if (result && typeof result === 'object' && key in result) {
            result = (result as Record<string, unknown>)[key];
        } else {
            return path; // Return path if not found
        }
    }

    return typeof result === 'string' ? result : path;
}

/**
 * Custom hook for translations and currency formatting
 */
export function useTranslation() {
    const locale = useStore((state) => state.locale);
    const currency = useStore((state) => state.currency);

    /**
     * Translate a key to the current locale
     * Supports interpolation: t('scan.productAdded', { product: 'Apple' })
     */
    const t = (key: string, params?: Record<string, string | number>): string => {
        const translation = getNestedValue(translations[locale] as unknown as Record<string, unknown>, key);

        if (!params) return translation;

        // Replace {param} placeholders with values
        return Object.entries(params).reduce(
            (str, [param, value]) => str.replace(new RegExp(`\\{${param}\\}`, 'g'), String(value)),
            translation
        );
    };

    /**
     * Format a price in cents to the current currency
     */
    const formatPrice = (priceInCents: number): string => {
        const amount = priceInCents / 100;
        const currencyLocale = currencyLocales[currency];

        return new Intl.NumberFormat(currencyLocale, {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(amount);
    };

    /**
     * Get the current currency symbol
     */
    const getCurrencySymbol = (): string => {
        return currencySymbols[currency];
    };

    /**
     * Check if current locale is RTL
     */
    const isRTL = locale === 'he';

    return {
        t,
        formatPrice,
        getCurrencySymbol,
        locale,
        currency,
        isRTL,
    };
}
