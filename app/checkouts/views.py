import helpers.billing
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django.contrib import messages


from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription

User = get_user_model()

BASE_URL = settings.BASE_URL

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id #Duda
    print("price_id", price_id)
    return redirect("stripe-checkout-start")

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get("checkout_subscription_price_id")
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj = None
    print("Checkout Subscription Price ID:", checkout_subscription_price_id) #Duda
    if checkout_subscription_price_id is None or obj is None:        
        return redirect("/pricing")

    customer_stripe_id = request.user.customer.stripe_id
    print("customer_stripe_id", customer_stripe_id) #Duda    

    success_url_path = reverse("stripe-checkout-end")
    pricing_url_path = reverse("pricing")
    price_stripe_id = obj.stripe_id

    success_url = f"{BASE_URL}{success_url_path}"
    cancel_url= f"{BASE_URL}{pricing_url_path}"

    url = helpers.billing.start_checkout_session(
        customer_stripe_id,
         success_url=success_url,
         cancel_url=cancel_url,
         price_stripe_id=price_stripe_id,
         raw=False
    ) 
    
    return redirect(url)


@login_required
def checkout_finalize_view(request):
    
    session_id = request.GET.get('session_id')
    #print("Esta Session ID es para pruebas:", session_id)

    checkout_data = helpers.billing.get_checkout_customer_plan(session_id)
    
    customer_id = checkout_data.pop("customer_id")
    #print("customer_id", customer_id)

    sub_plan = checkout_data.pop("plan_id")
    #print("sub_plan", sub_plan)

    sub_stripe_id = checkout_data.pop("sub_stripe_id")
    #print("sub_stripe_id", sub_stripe_id)
    
    subscription_data = {**checkout_data}
    #for k, v in subscription_data.items():
    #    print(f"{k}: {v}")

    try:
        sub_obj = Subscription.objects.get(subscriptionprice__stripe_id=sub_plan)     
    except:
        sub_obj = None
        print("El objeto: sub_obj .. no es nulo")  

    #print("sub_obj", sub_obj.price)  
    
    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id)
    except:
        user_obj = None
        print("Este user no se ha creado: user_obj")
    #print("user_obj", user_obj)
    
    _user_sub_exists = False

    updated_sub_options = {
        "subscription": sub_obj,
        "stripe_id": sub_stripe_id,
        "user_cancelled": False,
        **subscription_data,
    }
        
    #for k, v in updated_sub_options.items():
    #    print(f"{k}: {v}")

    try:
        _user_sub_obj = UserSubscription.objects.get(user=user_obj)
        _user_sub_exists = True

    except UserSubscription.DoesNotExist:
        _user_sub_obj = UserSubscription.objects.create(
                    user=user_obj, 
                    **updated_sub_options
                    )
        print("El objeto UserSubscription se ha creado por defecto")
    except:
        _user_sub_obj = None
        print("El objeto UserSubscription se ha creado por defecto 2")
    
    if None in [sub_obj, user_obj, _user_sub_obj]:
        return HttpResponseBadRequest("Invalid subscription or user data.Please contact us for support.")

    print("comienza segunda parte de la vista")

    if _user_sub_exists:
        # cancel old subscription
        old_stripe_id = _user_sub_obj.stripe_id

        same_stripe_id = sub_stripe_id == old_stripe_id 

        #print("Subscription updated for user:", _user_sub_obj.user)
        #print("Entra aca", _user_sub_exists)

        if old_stripe_id is not None and not same_stripe_id:
            try:
                helpers.billing.cancel_subscription(
                old_stripe_id,
                reason="Auto ended by new subscription",
                feedback="other")
            except:    
                pass        

        #assign new subscription
        for k, v in updated_sub_options.items():
            setattr(_user_sub_obj, k, v)
            # print(f"clave: {k}: valor: {v}")

        _user_sub_obj.save()
        messages.success(request, "Success!! You have joined us!")
        return redirect(_user_sub_obj.get_absolute_url())
        # print("existe?-->", _user_sub_exists)

        
        print("Subscription updated for user:", _user_sub_obj.user)
        print("Subscription updated for stripe_id:", _user_sub_obj.stripe_id)
        print("Subscription updated for current_period_start:", _user_sub_obj.current_period_start)
        print("Subscription updated for current_period_end:", _user_sub_obj.current_period_end)
        #print("Subscription updated price:", sub_obj.price)
        #print("Subscription updated for current_period_end:", _user_sub_obj.currency)        
        
    context = {"subscription": _user_sub_obj}
    return render(request, "checkout/success.html", context)
    
