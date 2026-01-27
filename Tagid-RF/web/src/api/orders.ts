/**
 * Orders API service
 * Fetches order history from the backend
 */

import { API_BASE_URL } from './config';

export interface OrderItem {
    productId: string;
    productName: string;
    quantity: number;
    priceInCents: number;
}

export interface Order {
    id: string;
    createdAt: string;
    status: string;
    totalInCents: number;
    currency: string;
    provider: string;
    items: OrderItem[];
}

export interface OrdersListResponse {
    orders: Order[];
    total: number;
}

/**
 * Fetch all orders for the current user
 */
export async function fetchOrders(): Promise<OrdersListResponse> {
    const token = localStorage.getItem('authToken');

    if (!token) {
        throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/orders/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || 'Failed to fetch orders');
    }

    return response.json();
}

/**
 * Fetch a single order by ID
 */
export async function fetchOrderById(orderId: string): Promise<Order> {
    const token = localStorage.getItem('authToken');

    if (!token) {
        throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || 'Failed to fetch order');
    }

    return response.json();
}
