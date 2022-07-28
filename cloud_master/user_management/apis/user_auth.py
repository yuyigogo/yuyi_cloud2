import logging

from customer.services.customer_service import CustomerService
from django.contrib.auth import login, logout
from mongoengine import DoesNotExist
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from sites.services.site_service import SiteService
from user_management.models.mongo_token import MongoToken
from user_management.models.user import CloudUser
from user_management.models.user_session import UserSession
from user_management.services.user_token_service import UserTokenService
from user_management.validators.user_login_serializers import \
    LoginViewViewSerializer

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class LoginView(BaseView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @staticmethod
    def _add_cloud_token_in_request_header(request: Request) -> MongoToken:
        try:
            token = UserTokenService.get_token_by_user_id(user_id=request.user.pk)
            token.emit_key()
        except DoesNotExist:
            token = MongoToken(user=request.user).save()
        finally:
            # in order to get the latest token for FE, set token into request header
            request.META["HTTP_X_AUTH_TOKEN"] = token.key
        return token

    def post(self, request):
        print(111)
        data, _ = self.get_validated_data(LoginViewViewSerializer)
        logger.info(f"{request.user.username} request login with {data=}")
        try:
            user = CloudUser.objects.get(
                username=data["username"], password=data["password"]
            )
        except DoesNotExist:
            logger.info(f"login failed with {data=}")
            return BaseResponse(
                status_code=HTTP_400_BAD_REQUEST, msg="username or password error!",
            )
        if user.is_active:
            user.remove_sessions()
            login(request, user)
            # session may be flushed after auth_login(), in this case, generate a new session key
            if not request.session.session_key:
                request.session.cycle_key()
            self._add_cloud_token_in_request_header(request)
            # note the new session of user
            UserSession(user_id=user.id, session_key=request.session.session_key).save()
            current_user = {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_cloud_super_admin": user.is_cloud_super_admin(),
                "is_client_super_admin": user.is_client_super_admin(),
                "customer": str(user.customer),
                "role_level": user.role_level,
                "customer_info": CustomerService.get_customer_info(user.customer),
                "site_info": SiteService.get_user_sites_info(user.sites),
            }
            return BaseResponse(data=current_user)
        else:
            logger.info(f"{user.username} is not active!")
            return BaseResponse(
                status_code=HTTP_400_BAD_REQUEST, msg="user login failed!",
            )

    def get(self, request):
        # redirect to login template.
        return BaseResponse(status_code=HTTP_200_OK)


class LogOutView(BaseView):
    def post(self, request):
        user = request.user
        logger.info(f"{user.username} request logout!")
        UserTokenService.get_token_by_user_id(user_id=user.pk).delete()
        user.remove_sessions()
        logout(request)
        # redirect to login template.
        return BaseResponse(status_code=HTTP_200_OK)
