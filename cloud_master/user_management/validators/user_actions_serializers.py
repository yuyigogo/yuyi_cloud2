from mongoengine import DoesNotExist

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
                raise APIException("请选择公司！")
            if Customer.objects(id=customer).count() != 1:
                raise APIException("公司不存在！")
            if role_level == RoleLevel.NORMAL.value:
                sites = data.get("sites")
                if not sites:
                    raise APIException("请选择站点！")
                num = Site.objects.filter(customer=customer, id__in=sites).count()
                if num != len(sites):
                    raise APIException("站点不存在！")
        return data


class UsersDeleteSerializer(BaseSerializer):
    user_id = CharField(required=True)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        user_id = data["user_ids"]
        if str(user.id) == user_id:
            raise APIException("禁止修改自己！")
        try:
            d_user = CloudUser.objects.get(id=user_id)
        except DoesNotExist:
            raise APIException("invalid user_id!")
        data["d_user"] = d_user
        if user.role_level >= d_user.role_level:
            raise ForbiddenException("无此操作权限！")
        return data


class PutUsersSerializer(UserCreateSerializer):
    is_suspend = BooleanField(required=False)
    user_id = CharField(required=True)

    def validated_user_id(self, user_id):
        try:
            update_user = CloudUser.objects.get(id=user_id)
        except DoesNotExist:
            raise APIException("invalid user_id!")
        self.context["update_user"] = update_user
        return user_id

    def validate(self, data: dict) -> dict:
        super(UserCreateSerializer, self).validate(data)
        return data
