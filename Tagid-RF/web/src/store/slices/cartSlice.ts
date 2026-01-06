import { StateCreator } from 'zustand';
import { CartItem, MoneyCents } from '../types';
import { CatalogSlice } from './catalogSlice';

export interface CartSlice {
  items: CartItem[];
  addByProductId: (productId: string, qty?: number) => void;
  addByBarcode: (barcode: string, qty?: number) => boolean;
  setQty: (productId: string, qty: number) => void;
  remove: (productId: string) => void;
  clear: () => void;
  getTotalInCents: () => MoneyCents;
  getCartItemCount: () => number;
}

export const createCartSlice: StateCreator<
  CartSlice & CatalogSlice,
  [],
  [],
  CartSlice
> = (set, get) => ({
  items: [],

  addByProductId: (productId: string, qty = 1) => {
    const existingItem = get().items.find((i) => i.productId === productId);
    if (existingItem) {
      set({
        items: get().items.map((i) =>
          i.productId === productId
            ? { ...i, qty: Math.min(i.qty + qty, 99) }
            : i
        ),
      });
    } else {
      set({ items: [...get().items, { productId, qty }] });
    }
  },

  addByBarcode: (barcode: string, qty = 1) => {
    const product = get().getProductByBarcode(barcode);
    if (!product) {
      return false;
    }
    get().addByProductId(product.id, qty);
    return true;
  },

  setQty: (productId: string, qty: number) => {
    const clampedQty = Math.max(1, Math.min(qty, 99));
    set({
      items: get().items.map((i) =>
        i.productId === productId ? { ...i, qty: clampedQty } : i
      ),
    });
  },

  remove: (productId: string) => {
    set({ items: get().items.filter((i) => i.productId !== productId) });
  },

  clear: () => {
    set({ items: [] });
  },

  getTotalInCents: () => {
    return get().items.reduce((total, item) => {
      const product = get().getProductById(item.productId);
      return total + (product ? product.priceInCents * item.qty : 0);
    }, 0);
  },

  getCartItemCount: () => {
    return get().items.reduce((count, item) => count + item.qty, 0);
  },
});

