from typing import Union

from bson import ObjectId
from user_management.models.mongo_token import MongoToken

from common.framework.service import BaseService


class UserTokenService(BaseService):
    @classmethod
    def get_token_by_user_id(cls, user_id: Union[str, ObjectId]) -> MongoToken:
        return MongoToken.objects.get(user=user_id)

    @classmethod
    def get_token_by_key(cls, key: str) -> MongoToken:
        return MongoToken.objects.get(key=key)

    @classmethod
    def delete_token_by_user_id(cls, user_id: Union[str, ObjectId]):
        MongoToken.objects.filter(user=user_id).delete()
