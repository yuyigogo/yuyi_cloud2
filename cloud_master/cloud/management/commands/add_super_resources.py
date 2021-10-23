from django.core.management import BaseCommand

from common.const import RoleLevel, ALL
from customer.services.customer_service import CustomerService
from sites.models.site import Site
from user_management.models.user import CloudUser


class Command(BaseCommand):
    help = "create a super admin"

    def handle(self, *args, **options):
        self.stdout.write("You are creating a super admin and named ALL customer/site")
        if CloudUser.objects(role_level=RoleLevel.CLOUD_SUPER_ADMIN).count() > 0:
            self.stdout.write("super admin has existed!")
            return
        customer = CustomerService.create_customer(
            ALL, administrative_division="Chines", remarks="this is named ALL customer"
        )
        site = Site(
            name=ALL,
            customer=customer.pk,
            administrative_division="Chines",
            voltage_level="220V",
            site_location=[110, 110],
            remarks="this is named all Site.",
        )
        site.save()
        super_user = CloudUser(
            username="cloud super admin",
            password="1234567890",
            customer=customer.pk,
            sites=[site.pk],
            phone="110",
            email="110@gmail.com",
            role_level=RoleLevel.CLOUD_SUPER_ADMIN,
        )
        super_user.save()
        self.stdout.write("create success!")
