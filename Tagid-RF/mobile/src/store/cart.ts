// src/store/cart.ts
import { create } from 'zustand';

export type CartItem = { id: string; title: string; priceInCents: number; qty: number }

type CartState = {
  items: CartItem[]
  add: (item: Omit<CartItem, 'qty'>) => void
  inc: (id: string) => void
  dec: (id: string) => void
  clear: () => void
}

export const useCart = create<CartState>((set) => ({
  items: [],
  add: (item) => set((s) => {
    console.log("✅ Adding item to cart:", item)
    const i = s.items.find(x => x.id === item.id)
    return i ? { items: s.items.map(x => x.id===item.id ? {...x, qty:x.qty+1} : x) }
             : { items: [...s.items, { ...item, qty: 1 }] }
  }),
  inc: (id) => set((s) => {
    console.log("➕ Incrementing item:", id)
    return { items: s.items.map(x => x.id===id? {...x, qty:x.qty+1}:x)}
  }),
  dec: (id) => set((s) => {
    console.log("➖ Decrementing item:", id)
    const item = s.items.find(x => x.id === id)
    if (!item) return s
    
    // If quantity would be 0, remove the item
    if (item.qty <= 1) {
      console.log("🗑️ Removing item from cart:", id)
      return { items: s.items.filter(x => x.id !== id) }
    }
    
    // Otherwise just decrement
    return { items: s.items.map(x => x.id===id? {...x, qty:x.qty-1}:x)}
  }),
  clear: () => {
    console.log("🧹 Clearing cart")
    return { items: [] }
  },
}))