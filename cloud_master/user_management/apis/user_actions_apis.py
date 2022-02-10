import logging

from customer.services.customer_service import CustomerService
from mongoengine import DoesNotExist
from rest_framework.status import HTTP_201_CREATED
from sites.services.site_service import SiteService
from user_management.services.user_service import UserService
from user_management.services.user_token_service import UserTokenService
from user_management.validators.user_actions_serializers import (
    PutUsersSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UsersDeleteSerializer,
)

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class UsersView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            RoleLevel.ADMIN.value,
        ),
    )

    def get(self, request):
        """
        get list users
        :param request:
        :return:
        """
        user = request.user
        data, _ = self.get_validated_data(UserListSerializer)
        logger.info(f"{user.username} request list of users with {data=}")
        username = data.get("username")
        customer = data.get("customer")
        sites = data.get("sites")
        page = data.get("page", 1)
        limit = data.get("limit", 20)
        total, user_info = UserService(user).get_users(
            page, limit, username, customer, sites
        )
        return BaseResponse(data={"total": total, "users": user_info})

    def post(self, request):
        """
        create new user
        :param request:
        :return:
        """
        data, _ = self.get_validated_data(UserCreateSerializer)
        logger.info(
            f"{request.user.username} request to create a new user with {data=}"
        )
        user = UserService.create_user(data)
        logger.info(f"crete new user: {user.id} successfully!")
        return BaseResponse(data=user.to_dict(), status_code=HTTP_201_CREATED)

    def put(self, request):
        user = request.user
        data, context = self.get_validated_data(PutUsersSerializer)
        update_user = context["update_user"]
        logger.info(f"{user.username} request update users: with {data=}")
        is_suspend = data.get("is_suspend")
        if is_suspend is not None:
            update_user.update(is_active=is_suspend)
            return BaseResponse()
        UserService.update_user(
            update_user,
            data["role_level"],
            password=data.get("password"),
            customer=data.get("customer"),
            sites=data.get("sites")
        )
        return BaseResponse()

    def delete(self, request):
        user = request.user
        data, _ = self.get_validated_data(UsersDeleteSerializer)
        d_user = data["d_user"]
        delete_user_id = data["user_id"]
        logger.info(f"{user.username} request delete users: {delete_user_id}")
        d_user.delete()
        return BaseResponse()


class CurrentUserView(BaseView):
    def get(self, request):
        user = request.user
        try:
            token = UserTokenService.get_token_by_user_id(user_id=user.id)
            token_key = token.key
        except DoesNotExist:
            token_key = ""
        current_user = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_cloud_super_admin": user.is_cloud_super_admin(),
            "is_client_super_admin": user.is_client_super_admin(),
            "customer": str(user.customer),
            "token": token_key,
            "role_level": user.role_level,
            "customer_info": CustomerService.get_customer_info(user.customer),
            "site_info": SiteService.get_user_sites_info(user.sites),
        }
        return BaseResponse(data=current_user)
