from rest_framework.fields import CharField

from common.const import MAX_LENGTH_NAME
from common.framework.serializer import BaseSerializer


class LoginViewViewSerializer(BaseSerializer):
    username = CharField(max_length=MAX_LENGTH_NAME)
    password = CharField()
