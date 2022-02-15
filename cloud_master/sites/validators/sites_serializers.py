from bson import ObjectId
from mongoengine import DoesNotExist
from rest_framework.fields import BooleanField, CharField, ListField, IntegerField
from sites.models.site import Site

from common.const import ALL, MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.error_code import StatusCode
from common.framework.exception import (
    APIException,
    ForbiddenException,
    InvalidException,
)
from common.framework.serializer import AdministrativeDivisionSerializer, BaseSerializer


def get_site(site_id: str) -> Site:
    try:
        site = Site.objects.get(id=site_id)
    except DoesNotExist:
        raise InvalidException(f"invalid {site_id=}")
    return site


class GetCustomerSitesSerializer(BaseSerializer):
    def validate(self, data: dict) -> dict:
        customer_id = self.context["customer_id"]
        user = self.context["request"].user
        if user.is_cloud_or_client_super_admin():
            return data
        else:
            if str(user.customer_id) != customer_id:
                raise ForbiddenException(
                    "user can't get not belong to its own customer's sits"
                )
            return data


class CreateSiteSerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    administrative_division = AdministrativeDivisionSerializer(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)
    voltage_level = CharField(required=True)
    site_location = ListField(required=True)

    def validate(self, data: dict) -> dict:
        name = data["name"]
        customer_id = self.context["customer_id"]
        if (
            name == ALL
            or Site.objects.filter(customer=customer_id, name=name).count() > 0
        ):
            raise APIException(
                "站点名称已存在!", code=StatusCode.SITE_NAME_DUPLICATE.value,
            )
        return data


class BaseSiteSerializer(BaseSerializer):
    def validate(self, data: dict) -> dict:
        customer_id = self.context["customer_id"]
        site_id = self.context["site_id"]
        user = self.context["request"].user
        site = get_site(site_id)
        if (
            not user.is_cloud_or_client_super_admin()
            and str(site.customer) != customer_id
        ):
            raise ForbiddenException(
                f"user can't get not belong to its own customer's sits"
            )
        self.context["site"] = site
        return data


class UpdateSiteSerializer(BaseSerializer):
    name = CharField(max_length=MAX_LENGTH_NAME)
    administrative_division = AdministrativeDivisionSerializer()
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)
    voltage_level = CharField()
    site_location = ListField(required=False)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        site_id = self.context["site_id"]
        site = get_site(site_id)
        self.context["site"] = site
        name = data.get("name")
        if name and name != site.name:
            if Site.objects.filter(name=name).count() > 0:
                raise APIException(
                    "站点名称已存在!", code=StatusCode.SITE_NAME_DUPLICATE.value,
                )
        if user.is_cloud_or_client_super_admin():
            return data
        else:
            if ObjectId(site_id) not in user.sites:
                raise ForbiddenException("user can't modify not belong to its own sits")
        return data


class DeleteSiteSerializer(BaseSerializer):
    clear_resource = BooleanField(default=False)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        site_id = self.context["site_id"]
        site = get_site(site_id)
        self.context["site"] = site
        if site.name == ALL:
            raise ForbiddenException("named ALL site can not be deleted!")
        if user.is_cloud_or_client_super_admin():
            return data
        else:
            if ObjectId(site_id) not in user.sites:
                raise ForbiddenException("user can't modify not belong to its own sits")
        return data
