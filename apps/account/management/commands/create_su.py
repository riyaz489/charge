from django.core.management.base import BaseCommand
from apps.account.models import Account
import os

user = os.environ['ADMIN_NAME']
password = os.environ['ADMIN_PASS']


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not Account.objects.filter(username="admin").exists():
            Account.objects.create_superuser("chargeapplication@gmail.com",str(user),  str(password))