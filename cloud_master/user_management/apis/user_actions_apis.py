import logging

from rest_framework.status import HTTP_201_CREATED
from user_management.services.user_service import UserService
from user_management.validators.user_actions_serializers import (
    UserCreateSerializer, UserListSerializer)

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class UsersView(BaseView):
    permission_classes = PermissionFactory(
        RoleLevel.SUPER_ADMIN, RoleLevel.ADMIN, method_list=("POST",)
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
        pass
