import { StateCreator } from 'zustand';
import { Product } from '../types';

export interface CatalogSlice {
  products: Product[];
  isLoaded: boolean;
  loadProducts: (products: Product[]) => void;
  getProductById: (id: string) => Product | undefined;
  getProductByBarcode: (barcode: string) => Product | undefined;
  searchProducts: (query: string) => Product[];
}

export const createCatalogSlice: StateCreator<CatalogSlice> = (set, get) => ({
  products: [],
  isLoaded: false,

  loadProducts: (products: Product[]) => {
    set({ products, isLoaded: true });
  },

  getProductById: (id: string) => {
    return get().products.find((p) => p.id === id);
  },

  getProductByBarcode: (barcode: string) => {
    return get().products.find((p) => p.barcode === barcode);
  },

  searchProducts: (query: string) => {
    const lowerQuery = query.toLowerCase();
    return get().products.filter(
      (p) =>
        p.name.toLowerCase().includes(lowerQuery) ||
        p.barcode.includes(query) ||
        (p.sku && p.sku.toLowerCase().includes(lowerQuery))
    );
  },
});

