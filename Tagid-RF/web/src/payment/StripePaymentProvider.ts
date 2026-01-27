import { PaymentResult } from './types';

export async function payWithStripe(
    orderId: string,
    amount: number,
    currency: string = 'ILS'
): Promise<PaymentResult> {
    const token = localStorage.getItem('authToken');
    if (!token || token === 'demo-token') {
        return { ok: false, orderId, error: 'אנא התחבר למערכת כדי להשלים את הרכישה' };
    }

    try {
        const response = await fetch('/api/v1/payment/create-intent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                order_id: orderId,
                amount: amount,
                currency: currency,
                payment_provider: 'STRIPE',
                metadata: {} // Ensure metadata is sent to satisfy Pydantic validation
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create payment intent');
        }

        const data = await response.json();
        return {
            ok: true,
            orderId: orderId,
            clientSecret: data.client_secret,
            paymentId: data.payment_id
        };
    } catch (error: any) {
        console.error('Stripe payment error:', error);
        return { ok: false, orderId, error: error.message };
    }
}

/**
 * Confirm payment after Stripe confirms it client-side.
 * This updates the payment status in our database to COMPLETED.
 */
export async function confirmPayment(paymentId: string): Promise<{ ok: boolean; error?: string }> {
    const token = localStorage.getItem('authToken');
    if (!token) {
        return { ok: false, error: 'Not authenticated' };
    }

    try {
        const response = await fetch('/api/v1/payment/confirm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                payment_id: paymentId,
                payment_method_id: null  // Already confirmed by Stripe client-side
            })
        });

        if (!response.ok) {
            const error = await response.json();
            console.warn('Failed to confirm payment in backend:', error);
            // Don't throw - payment was already successful in Stripe
            return { ok: false, error: error.detail };
        }

        return { ok: true };
    } catch (error: any) {
        console.warn('Error confirming payment:', error);
        return { ok: false, error: error.message };
    }
}
