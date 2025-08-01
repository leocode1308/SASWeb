"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import home_view, about_view, pw_protected_view, user_only_view, staff_only_view
from auth.views import login_view, register_view
from checkouts import views as checkout_views
from subscriptions import views as subscription_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home_view'),
    path('about/', about_view, name='about_view'),

    path("checkout/sub-price/<int:price_id>/", 
            checkout_views.product_price_redirect_view,
            name='sub-price-checkout'
            ),
    path("checkout/start/", 
            checkout_views.checkout_redirect_view,
            name='stripe-checkout-start'
            ),
    path("checkout/success/", 
            checkout_views.checkout_finalize_view,
            name='stripe-checkout-end'
            ),
            
    #path('login/', login_view, name='login_view'),
    path('pricing/', subscription_views.subscription_price_view, name='pricing'),
    path('pricing/<str:interval>', subscription_views.subscription_price_view, name='pricing_interval'),
    #path('register/', register_view, name='register_view'),
    
    path('accounts/billing/', subscription_views.user_subscription_view, name='user_subscription'),
    path('accounts/billing/cancel', subscription_views.user_cancel_view, name='user_subscription_cancel'),
    path('accounts/', include('allauth.urls')),
    path('protected/', pw_protected_view, name='pw_protected_view'),
    path('protected/user-only/', user_only_view, name='user_only_view'),
    path('protected/staff-only/', staff_only_view),
    path('profiles/', include('profiles.urls')),
]
