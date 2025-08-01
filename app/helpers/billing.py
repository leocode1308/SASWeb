# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from decouple import config
from .date_utils import time_stamp_to_datetime

DJANGO_DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="", cast=str)

if "sk_test_" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("You are using a test Stripe key in production. Please use your live secret key.")

stripe.api_key = STRIPE_SECRET_KEY

def serialize_subscription_data(subscription_response):
    """
    Serializes the subscription data to a dictionary format.
    """
    status = subscription_response.status

    first_subscription_item = None
    if subscription_response and 'items' in subscription_response and subscription_response['items'] and 'data' in subscription_response['items'] and len(subscription_response['items']['data']) > 0:
        first_subscription_item = subscription_response['items']['data'][0]

    if first_subscription_item:
        current_period_start_timestamp = first_subscription_item.get('current_period_start')
        current_period_end_timestamp = first_subscription_item.get('current_period_end')

        if current_period_start_timestamp is not None:
            current_period_start = time_stamp_to_datetime(current_period_start_timestamp)
        else:
            current_period_start = None # O un valor predeterminado si es apropiado
            print("Advertencia: 'current_period_start' no encontrado o es None en el ítem de la suscripción.")

        if current_period_end_timestamp is not None:
            current_period_end = time_stamp_to_datetime(current_period_end_timestamp)
        else:
            current_period_end = None # O un valor predeterminado si es apropiado
            print("Advertencia: 'current_period_end' no encontrado o es None en el ítem de la suscripción.")
    else:
        current_period_start = None
        current_period_end = None
        print("Advertencia: No se encontraron ítems de datos válidos en la suscripción de Stripe.")

    cancel_at_period_end = subscription_response.cancel_at_period_end 
    return {
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
        "status": status,
        "cancel_at_period_end": cancel_at_period_end,
        }

def create_customer(name="", email="", metadata={}, raw=False):
    response = stripe.Customer.create(
        name=name,
        email=email,
        metadata=metadata,
    )
    if raw:
        return response
    stripe_id = response.id 
    return stripe_id

def create_product(name="", metadata={}, raw=False):
    response = stripe.Product.create(
        name=name,
        metadata=metadata,
    )
    if raw:
        return response
    stripe_id = response.id 
    return stripe_id

def create_price(currency="usd",  unit_amount="9999", interval="month", product=None, metadata={}, raw=False):
    if product is None:
        return None
    response = stripe.Price.create(
            currency=currency,
            unit_amount=unit_amount,
            recurring={"interval": interval},
            product=product,
            metadata=metadata
        )
    if raw:
        return response
    stripe_id = response.id 
    return stripe_id

def start_checkout_session(customer_id, success_url="", cancel_url="", price_stripe_id="", raw=True):
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        success_url = f"{success_url}" + "?session_id={CHECKOUT_SESSION_ID}"
    response= stripe.checkout.Session.create(
        customer=customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_stripe_id, "quantity": 1}],
        mode="subscription",
    )
    if raw:
        return response
    return response.url

def get_checkout_session(stripe_id, raw=True):
    response =  stripe.checkout.Session.retrieve(
            stripe_id
        )
    if raw:
        return response
    return response.url

def get_subscription(stripe_id, raw=True):
    response =  stripe.Subscription.retrieve(
            stripe_id
        )
    if raw:
        return response
    return serialize_subscription_data(response)

def get_customer_active_subscriptions(stripe_id):
    response =  stripe.Subscription.list(
            customer=stripe_id,
            status="active",
            
        )
    return response

def cancel_subscription(stripe_id, reason="", 
                        feedback = "other",
                        cancel_at_period_end=False,
                        raw=True):
    if cancel_at_period_end:
        response =  stripe.Subscription.modify(
            stripe_id,
            cancel_at_period_end=cancel_at_period_end,
            cancellation_details={
                "comment": reason,
                "feedback": feedback
            }
        )
    else:
        response =  stripe.Subscription.cancel(
            stripe_id,
            cancellation_details={
                "comment": reason,
                "feedback": feedback
            }
        )
    if raw:
        return response
    return serialize_subscription_data(response)

def start_checkout_session(customer_id, 
        success_url="", 
        cancel_url="", 
        price_stripe_id="", 
        raw=True):
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        success_url = f"{success_url}" + "?session_id={CHECKOUT_SESSION_ID}"
    response= stripe.checkout.Session.create(
        customer=customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_stripe_id, "quantity": 1}],
        mode="subscription",
    )
    if raw:
        return response
    return response.url

def get_checkout_customer_plan(session_id):
    checkout_r = get_checkout_session(session_id, raw=True)
    customer_id = checkout_r.customer
    sub_stripe_id = checkout_r.subscription
    sub_r = get_subscription(sub_stripe_id, raw=True) 
    sub_plan = sub_r.plan.id
    status = sub_r.status
    subscription_data = serialize_subscription_data(sub_r)

    data = {
        "customer_id": customer_id,
        "plan_id": sub_plan,
        "sub_stripe_id": sub_stripe_id,
        **subscription_data,
    }
    return data 
