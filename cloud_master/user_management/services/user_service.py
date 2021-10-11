from common.framework.service import BaseService
from user_management.models.user import CloudUser


class UserService(BaseService):
    def __init__(self):
        pass

    @classmethod
    def create_user(cls, user_data: dict) -> CloudUser:
        user = CloudUser(**user_data)
        user.save()
        return user
