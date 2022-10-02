from common.const import ALL
from customer.models.customer import Customer
from mongoengine import DoesNotExist

from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer
from sites.models.site import Site


class CustomerAssetSerializer(BaseSerializer):
    is_refresh = B
    def validate(self, data):
        customer_id = self.context["customer_id"]
        try:
            customer = Customer.objects.get(pk=customer_id)
        except DoesNotExist:
            raise APIException(f"invalid {customer_id=}")
        data["customer"] = customer
        return data


class SiteAssetSerializer(BaseSerializer):
    def validate(self, data):
        site_id = self.context["site_id"]
        try:
            site = Site.objects.get(pk=site_id)
        except DoesNotExist:
            raise APIException(f"invalid {site_id=}")
        if site.name == ALL:
            raise APIException("can't pass named all site id")
        return data
