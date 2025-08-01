from django.contrib import admin
from .models import Subscription, SubscriptionPrice, UserSubscription

# Register your models here.

class SubscriptionPrice(admin.TabularInline):
    model = SubscriptionPrice
    readonly_fields = ['stripe_id']
    can_delete = False
    extra = 0
    """
    fields = ['name', 'stripe_id', 'price', 'interval']
    readonly_fields = ['stripe_id', 'price', 'interval']
    """

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPrice]
    list_display = ['name', 'active', 'stripe_id']
    """
    search_fields = ('name',)
    list_filter = ('active',)
    """

admin.site.register(Subscription, SubscriptionAdmin)

admin.site.register(UserSubscription)

