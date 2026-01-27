import stripe
from app.core.config import get_settings
from typing import List, Dict, Any

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_checkout_session(items: List[Dict[str, Any]], success_url: str, cancel_url: str):
    """
    Create a Stripe Checkout Session for the items in the cart.
    """
    line_items = []
    for item in items:
        line_items.append({
            'price_data': {
                'currency': 'ils',
                'product_data': {
                    'name': item['name'],
                    'description': item.get('description', ''),
                },
                'unit_amount': int(item['price_in_cents']),
            },
            'quantity': item['qty'],
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return session
