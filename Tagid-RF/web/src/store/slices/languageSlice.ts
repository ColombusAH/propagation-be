import { StateCreator } from 'zustand';
import type { Locale, Currency } from '@/i18n';

export interface LanguageSlice {
    locale: Locale;
    currency: Currency;
    setLocale: (locale: Locale) => void;
    setCurrency: (currency: Currency) => void;
    toggleLocale: () => void;
}

export const createLanguageSlice: StateCreator<LanguageSlice> = (set, get) => ({
    locale: 'he', // Default to Hebrew
    currency: 'ILS', // Default to Israeli Shekel

    setLocale: (locale: Locale) => {
        set({ locale });
        // Update document direction for RTL support
        document.documentElement.dir = locale === 'he' ? 'rtl' : 'ltr';
        document.documentElement.lang = locale;
    },

    setCurrency: (currency: Currency) => {
        set({ currency });
    },

    toggleLocale: () => {
        const currentLocale = get().locale;
        const newLocale: Locale = currentLocale === 'he' ? 'en' : 'he';
        get().setLocale(newLocale);
    },
});
