from customer.models.customer import Customer
from mongoengine import DoesNotExist
from rest_framework.fields import BooleanField
from sites.models.site import Site

from common.const import ALL
from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer


class CustomerStatusSerializer(BaseSerializer):
    is_refresh = BooleanField(default=False)

    def validate(self, data):
        customer_id = self.context["customer_id"]
        try:
            customer = Customer.objects.get(pk=customer_id)
        except DoesNotExist:
            raise APIException(f"invalid {customer_id=}")
        if customer.name == ALL:
            raise APIException("can't pass named all's customer id")
        return data


class SiteStatusSerializer(BaseSerializer):
    is_refresh = BooleanField(default=False)

    def validate(self, data):
        site_id = self.context["site_id"]
        try:
            site = Site.objects.get(pk=site_id)
        except DoesNotExist:
            raise APIException(f"invalid {site_id=}")
        if site.name == ALL:
            raise APIException("can't pass named all's site id")
        return data
