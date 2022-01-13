from customer.models.customer import Customer
from mongoengine import DoesNotExist
from rest_framework.fields import (
    CharField,
    ChoiceField,
    EmailField,
    IntegerField,
    ListField,
    BooleanField,
)
from sites.models.site import Site
from sites.services.site_service import SiteService

from common.const import ALL, MAX_LENGTH_NAME, RoleLevel
from common.framework.exception import APIException, ForbiddenException
from common.framework.serializer import BaseSerializer
from user_management.models.user import CloudUser


class UserListSerializer(BaseSerializer):
    page = IntegerField(required=False)
    limit = IntegerField(required=False)
    username = CharField(required=False)
    customer = CharField(required=False)
    sites = ListField(child=CharField(), required=False)

    def validate(self, data: dict) -> dict:
        customer = data.get("customer")
        sites = data.get("sites")
        if customer is None and sites:
            raise APIException("invalid query parameters!")
        elif customer and sites:
            user = self.context["request"].user
            if user.is_cloud_or_client_super_admin():
                return data
            user_sites = set(map(user.sites, str))
            if str(user.customer) != customer:
                raise APIException("have no right to query this customer!")
            elif not set(sites).issubset(user_sites):
                raise APIException("have no right to query this sites!")
        return data


class UserCreateSerializer(BaseSerializer):
    username = CharField(max_length=MAX_LENGTH_NAME)
    password = CharField()
    email = EmailField()
    role_level = ChoiceField(choices=RoleLevel.allowed_role_level())
    customer = CharField()
    sites = ListField(
        child=CharField(), required=True, allow_empty=False, allow_null=False
    )
    phone = CharField(required=False)

    def validate_customer(self, customer: str) -> str:
        user = self.context["request"].user
        try:
            customer_obj = Customer.objects.get(id=customer)
        except DoesNotExist:
            raise APIException("invalid customer!")
        if customer_obj.name == ALL and not user.is_cloud_super_admin:
            raise APIException("have no right to choose this customer!")
        return customer

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        customer = data["customer"]
        sites = data["sites"]
        named_all_site = str(SiteService.named_all_site().id)
        if sites == [named_all_site] and not user.is_cloud_super_admin:
            raise APIException("have no right to choose this site!")
        num = Site.objects.filter(customer=customer, id__in=sites).count()
        if num != len(sites):
            raise APIException("invalid sites")
        return data


class UsersDeleteSerializer(BaseSerializer):
    user_ids = ListField(child=CharField(), required=True)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        user_ids = data["user_ids"]
        if str(user.id) in user_ids:
            raise APIException("should not delete yourself")
        user_role_levels = CloudUser.objects.filter(id__in=user_ids).values_list(
            "role_level"
        )
        if user.is_cloud_super_admin:
            return data
        elif user.is_client_super_admin():
            if (
                RoleLevel.CLOUD_SUPER_ADMIN.value in user_role_levels
                or RoleLevel.CLIENT_SUPER_ADMIN.value in user_role_levels
            ):
                raise ForbiddenException(
                    "forbidden to delete users with more permissions than yourself!"
                )
        else:
            # admin user
            if RoleLevel.ADMIN.value in user_role_levels:
                raise ForbiddenException(
                    "forbidden to delete users with more permissions than yourself!"
                )
        return data


class PutUsersSerializer(UsersDeleteSerializer):
    is_suspend = BooleanField(required=True)

    def validate(self, data: dict) -> dict:
        data = super(UsersDeleteSerializer, self).validate(data)
        return data
