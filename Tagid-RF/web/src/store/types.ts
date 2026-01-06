export type MoneyCents = number;

export interface Product {
  id: string;
  barcode: string;
  name: string;
  nameHe?: string; // Hebrew name for i18n
  priceInCents: MoneyCents;
  imageUrl?: string;
  sku?: string;
}

export interface CartItem {
  productId: string;
  qty: number;
}

export interface Order {
  id: string; // local uuid
  items: Array<{
    productId: string;
    qty: number;
    priceInCents: MoneyCents;
  }>;
  totalInCents: MoneyCents;
  customer: { name: string; email: string; note?: string };
  createdAt: string; // ISO
  status: 'PAID';
}

/**
 * Container (אמבטיה) - A physical container that can hold multiple products.
 * When scanned, all products inside are added to cart.
 */
export interface Container {
  id: string;
  barcode: string;           // QR/RFID identifier
  name: string;
  nameHe?: string;           // Hebrew name
  description?: string;
  products: Array<{
    productId: string;
    qty: number;
  }>;
  createdAt: string;         // ISO
  updatedAt: string;         // ISO
}

/**
 * Type of scanned item - used to distinguish between product and container
 */
export type ScanType = 'product' | 'container';

/**
 * Result of scanning a barcode/QR code
 */
export interface ScanResult {
  type: ScanType;
  id: string;
  barcode: string;
}


