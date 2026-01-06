import { StateCreator } from 'zustand';
import { Order } from '../types';

export interface OrdersSlice {
  orders: Order[];
  createOrder: (order: Order) => void;
  getById: (id: string) => Order | undefined;
  list: () => Order[];
}

export const createOrdersSlice: StateCreator<OrdersSlice> = (set, get) => ({
  orders: [],

  createOrder: (order: Order) => {
    set({ orders: [order, ...get().orders] });
  },

  getById: (id: string) => {
    return get().orders.find((o) => o.id === id);
  },

  list: () => {
    return get().orders;
  },
});

