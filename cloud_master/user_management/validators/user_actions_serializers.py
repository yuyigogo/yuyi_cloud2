from bson import ObjectId
from rest_framework.fields import CharField, ChoiceField, EmailField, ListField

from common.const import ALL, MAX_LENGTH_NAME, RoleLevel
from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer


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
