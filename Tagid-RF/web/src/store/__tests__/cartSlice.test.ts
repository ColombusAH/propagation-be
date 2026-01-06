import { describe, it, expect, beforeEach } from 'vitest';
import { create } from 'zustand';
import { createCatalogSlice } from '../slices/catalogSlice';
import { createCartSlice } from '../slices/cartSlice';
import { Product } from '../types';

const mockProducts: Product[] = [
  {
    id: 'p1',
    barcode: '123',
    name: 'Test Product 1',
    priceInCents: 100,
  },
  {
    id: 'p2',
    barcode: '456',
    name: 'Test Product 2',
    priceInCents: 200,
  },
];

describe('CartSlice', () => {
  let store: ReturnType<typeof create>;

  beforeEach(() => {
    store = create((...args) => ({
      ...createCatalogSlice(...args),
      ...createCartSlice(...args),
    }));

    // Load mock products
    store.getState().loadProducts(mockProducts);
  });

  it('should add product by ID', () => {
    const { addByProductId } = store.getState();

    addByProductId('p1');

    const state = store.getState();
    expect(state.items).toHaveLength(1);
    expect(state.items[0]).toEqual({ productId: 'p1', qty: 1 });
  });

  it('should add product by barcode', () => {
    const { addByBarcode } = store.getState();

    const success = addByBarcode('123');

    expect(success).toBe(true);
    const state = store.getState();
    expect(state.items).toHaveLength(1);
    expect(state.items[0]).toEqual({ productId: 'p1', qty: 1 });
  });

  it('should return false when adding unknown barcode', () => {
    const { addByBarcode } = store.getState();

    const success = addByBarcode('unknown');

    expect(success).toBe(false);
    expect(store.getState().items).toHaveLength(0);
  });

  it('should increment quantity when adding existing product', () => {
    const { addByProductId } = store.getState();

    addByProductId('p1');
    addByProductId('p1');

    const state = store.getState();
    expect(state.items).toHaveLength(1);
    expect(state.items[0].qty).toBe(2);
  });

  it('should set quantity', () => {
    const { addByProductId, setQty } = store.getState();

    addByProductId('p1');
    setQty('p1', 5);

    const state = store.getState();
    expect(state.items[0].qty).toBe(5);
  });

  it('should remove item', () => {
    const { addByProductId, remove } = store.getState();

    addByProductId('p1');
    addByProductId('p2');
    remove('p1');

    const state = store.getState();
    expect(state.items).toHaveLength(1);
    expect(state.items[0].productId).toBe('p2');
  });

  it('should clear cart', () => {
    const { addByProductId, clear } = store.getState();

    addByProductId('p1');
    addByProductId('p2');
    clear();

    expect(store.getState().items).toHaveLength(0);
  });

  it('should calculate total correctly', () => {
    const { addByProductId, getTotalInCents } = store.getState();

    addByProductId('p1', 2); // 2 * 100 = 200
    addByProductId('p2', 1); // 1 * 200 = 200

    expect(getTotalInCents()).toBe(400);
  });

  it('should count cart items correctly', () => {
    const { addByProductId, getCartItemCount } = store.getState();

    addByProductId('p1', 2);
    addByProductId('p2', 3);

    expect(getCartItemCount()).toBe(5);
  });

  it('should limit quantity to 99', () => {
    const { addByProductId, setQty } = store.getState();

    addByProductId('p1');
    setQty('p1', 150);

    const state = store.getState();
    expect(state.items[0].qty).toBe(99);
  });
});

