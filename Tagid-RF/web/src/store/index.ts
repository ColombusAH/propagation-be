import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { createCatalogSlice, CatalogSlice } from './slices/catalogSlice';
import { createCartSlice, CartSlice } from './slices/cartSlice';
import { createOrdersSlice, OrdersSlice } from './slices/ordersSlice';
import { createLanguageSlice, LanguageSlice } from './slices/languageSlice';
import { createContainerSlice, ContainerSlice } from './slices/containerSlice';

type StoreState = CatalogSlice & CartSlice & OrdersSlice & LanguageSlice & ContainerSlice;

export const useStore = create<StoreState>()(
  persist(
    (...args) => ({
      ...createCatalogSlice(...args),
      ...createCartSlice(...args),
      ...createOrdersSlice(...args),
      ...createLanguageSlice(...args),
      ...createContainerSlice(...args),
    }),
    {
      name: 'scan-and-pay-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Persist cart, orders, language preferences, and containers
        items: state.items,
        orders: state.orders,
        locale: state.locale,
        currency: state.currency,
        containers: state.containers,
        darkMode: state.darkMode,
      }),
      onRehydrateStorage: () => (state) => {
        // Apply RTL direction on app load
        if (state?.locale) {
          document.documentElement.dir = state.locale === 'he' ? 'rtl' : 'ltr';
          document.documentElement.lang = state.locale;
        }
      },
    }
  )
);


