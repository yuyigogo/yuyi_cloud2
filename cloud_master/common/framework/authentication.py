from typing import Optional

from mongoengine import DoesNotExist
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import NotAuthenticated
from user_management.models.mongo_token import MongoToken
from user_management.services.user_token_service import UserTokenService


class TokenAuthentication(BaseAuthentication):
    """
    setting in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES or class view
    """

    @staticmethod
    def validate_token(token: MongoToken) -> Optional[MongoToken]:
        """
        if token is expired and not beyond max expire days, new valid key will generate.
        :param token: the validate token
        :return: valid token
        """
        if not token.is_valid():
            if token.is_beyond_max_expire_days():
                return None
            token.emit_key()
        return token

    def authenticate_cloud_token(self, token_key: str):
        try:
            token = UserTokenService.get_token_by_key(key=token_key)
        except DoesNotExist:
            return None
        return self.validate_token(token)

    def authenticate(self, request):
        token_key = request.META.get("HTTP_X_AUTH_TOKEN")

        if not token_key:
            raise NotAuthenticated(
                "invalid authentication token", status.HTTP_401_UNAUTHORIZED
            )

        token = self.authenticate_cloud_token(token_key)
        if not token:
            raise NotAuthenticated(
                "invalid authentication token", status.HTTP_401_UNAUTHORIZED
            )
        request.META["HTTP_X_AUTH_TOKEN"] = token.key
        return token.user, token

    def authenticate_header(self, request):
        return "token_key"
