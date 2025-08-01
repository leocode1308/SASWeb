import helpers.billing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from subscriptions.models import SubscriptionPrice, UserSubscription
from subscriptions import utils as subs_utils

@login_required
def user_subscription_view(request):
    _user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("refresh sub")
        finished = subs_utils.refresh_active_users_subscriptions(user_ids=[request.user.id], active_only=False)  
        if finished:
            messages.success(request, "Your subscription has been refreshed successfully.")
        else:
            messages.error(request, "There was an error refreshing your subscription.Please try again.")
        return redirect(_user_sub_obj.get_absolute_url())
    return render(request, 'subscriptions/user_detail_view.html', {"subscription": _user_sub_obj})

@login_required
def user_cancel_view(request):
    _user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    #sub_data = _user_sub_obj.serialize()
    if request.method == "POST":
        print("refresh sub")
        if _user_sub_obj.stripe_id and _user_sub_obj.is_active_status:
            sub_data = helpers.billing.cancel_subscription(_user_sub_obj.stripe_id, 
                reason="User requested cancellation",
                feedback="other",
                cancel_at_period_end=True,
                raw = False)
            for k, v in sub_data.items():
                setattr(_user_sub_obj, k, v)
            _user_sub_obj.save()
            messages.success(request, "Your subscription has been cancelled successfully.")
        return redirect(_user_sub_obj.get_absolute_url())
    
    return render(request, 'subscriptions/user_cancel_view.html', {"subscription": _user_sub_obj})

# Create your views here.

def subscription_price_view(request, interval="month"):
    qs = SubscriptionPrice.objects.filter(featured=True)
    inv_mo = SubscriptionPrice.IntervalChoices.MONTHLY
    inv_yr = SubscriptionPrice.IntervalChoices.YEARLY
    object_list = qs.filter(interval=inv_mo)
    url_path_name = "pricing_interval"
    mo_url = reverse(url_path_name, kwargs={"interval": inv_mo})
    yr_url = reverse(url_path_name, kwargs={"interval": inv_yr})
    active = inv_mo
    if interval == inv_yr:
        active = inv_yr
        object_list = qs.filter(interval=inv_yr)
    return render(request, "subscriptions/pricing.html",
    {
        "object_list": object_list,
        "mo_url": mo_url,
        "yr_url": yr_url,
        "active": active,})