from customer.models.customer import Customer
from rest_framework.fields import (
    BooleanField,
    CharField,
    ChoiceField,
    EmailField,
    IntegerField,
    ListField,
)
from sites.models.site import Site
from user_management.models.user import CloudUser

from common.const import ALL, MAX_LENGTH_NAME, RoleLevel
from common.framework.exception import APIException, ForbiddenException
from common.framework.serializer import BaseSerializer


class UserListSerializer(BaseSerializer):
    page = IntegerField(required=False)
    limit = IntegerField(required=False)
    username = CharField(required=False)
    customer = CharField(required=False)
    sites = ListField(child=CharField(), required=False)

    # def validate(self, data: dict) -> dict:
    #     customer = data.get("customer")
    #     sites = data.get("sites")
    #     if customer is None and sites:
    #         raise APIException("invalid query parameters!")
    #     elif customer and sites:
    #         user = self.context["request"].user
    #         if user.is_cloud_or_client_super_admin():
    #             return data
    #         user_sites = set(map(user.sites, str))
    #         if str(user.customer) != customer:
    #             raise APIException("have no right to query this customer!")
    #         elif not set(sites).issubset(user_sites):
    #             raise APIException("have no right to query this sites!")
    #     return data


class UserCreateSerializer(BaseSerializer):
    username = CharField(max_length=MAX_LENGTH_NAME)
    password = CharField()
    email = EmailField()
    role_level = ChoiceField(choices=RoleLevel.allowed_role_level())
    customer = CharField(required=False)
    sites = ListField(
        child=CharField(), required=False, allow_empty=False, allow_null=False
    )
    phone = CharField(required=False)

    def validate(self, data: dict) -> dict:
        # 1. only normal user can't create new user:
        # 2. only cloud super admin can create client super admin;
        # 3. client super admin can have more then one;
        # 4. the same role level user can't modify the others;
        user = self.context["request"].user
        current_role_level = user.role_level
        role_level = data["role_level"]
        if current_role_level >= role_level:
            raise APIException("用户权限不够！")
        if role_level >= RoleLevel.ADMIN.value:
            customer = data.get("customer")
            if not customer:
                raise APIException("please choose customer!")
            if Customer.objects(id=customer).count() != 1:
                raise APIException("invalid customer!")
            if role_level == RoleLevel.NORMAL.value:
                sites = data.get("sites")
                if not sites:
                    raise APIException("please choose sites!")
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
        if user.role_level >= min(user_role_levels):
            raise ForbiddenException("无此操作权限！")
        return data


class PutUsersSerializer(UsersDeleteSerializer):
    is_suspend = BooleanField(required=True)

    def validate(self, data: dict) -> dict:
        data = super(UsersDeleteSerializer, self).validate(data)
        return data
