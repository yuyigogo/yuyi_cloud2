from bson import ObjectId
from rest_framework.fields import (CharField, ChoiceField, EmailField,
                                   IntegerField, ListField)

from common.const import ALL, MAX_LENGTH_NAME, RoleLevel
from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer


class UserListSerializer(BaseSerializer):
    page = IntegerField(required=False)
    limit = IntegerField(required=False)
    username = CharField(required=False)
    customer = CharField(required=False)
    sites = ListField(child=CharField(), required=False)

    def validate(self, data: dict) -> dict:
        customer = data.get("customer")
        sites = data.get("sites")
        if (customer and sites is None) or (customer is None and sites):
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
        if customer == ALL:
            # get named all customer
            return customer
        elif ObjectId.is_valid(customer):
            # get this customer
            return customer
        else:
            raise APIException("invalid customer!")

    def validate_sites(self, sites: list) -> list:
        if sites == [ALL]:
            # get named all customer
            return [sites]
        # todo validate sites in db
