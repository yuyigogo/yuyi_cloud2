from mongoengine import DoesNotExist, MultipleObjectsReturned
from rest_framework import status
from rest_framework.authentication import BaseAuthentication

from common.framework.exception import APIException


class TokenAuthentication(BaseAuthentication):
    """
    setting in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES or class view
    """

    def authenticate(self, request):
        token_key = (
            request.META.get("HTTP_X_AUTH_TOKEN")
            or request.GET.get("token_key")
            or request.data.get("token_key")
        )

        if not token_key:
            return None

        try:
            pass
            # token = MongoToken.objects.get(key=token_key)
        except (DoesNotExist, MultipleObjectsReturned) as e:
            raise APIException(
                "invalid authentication token", status.HTTP_401_UNAUTHORIZED
            )
        return token.user, token

    def authenticate_header(self, request):
        return "token_key"
