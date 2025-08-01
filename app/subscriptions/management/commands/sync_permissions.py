from django.core.management.base import BaseCommand
from typing import Any
from subscriptions.models import Subscription
import helpers.billing
from subscriptions import utils as subs_utils


class Command(BaseCommand):
    def handle(self, *args:Any, **options: Any):
        subs_utils.sync_subs_group_permissions()
        