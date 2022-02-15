from cloud.models import DocumentMixin
from mongoengine import (
    BinaryField,
    BooleanField,
    EmailField,
    IntField,
    ListField,
    ObjectIdField,
    StringField,
)
from user_management.models.user_session import UserSession

from common.const import MAX_LENGTH_NAME, RoleLevel
from vendor.django_mongoengine.mongo_auth.models import User
from vendor.django_mongoengine.sessions import MongoSession


class CloudUser(User, DocumentMixin):
    password = StringField(required=True, max_length=128)
    username = StringField(max_length=MAX_LENGTH_NAME, required=True)
    customer = ObjectIdField(required=False)
    sites = ListField(ObjectIdField(), default=[])
    phone = StringField(max_length=50)
    email = EmailField(required=True, max_length=100)
    avatar = BinaryField()
    role_level = IntField(required=True)
    is_active = BooleanField(default=True)

    def remove_sessions(self):
        user_sessions = UserSession.objects(user_id=self.id)
        for user_session in user_sessions:
            try:
                MongoSession.objects.get(session_key=user_session.session_key).delete()
            except:
                pass
            user_session.delete()

    def has_permissions(self, permissions: list) -> bool:
        """
        :param list permissions: list of permissions
        :return: if this user has any permission in permissions list
        :return: bool
        """
        has_perm = False
        if not permissions:
            # no permission needed
            has_perm = True
        elif self.role_level in permissions:
            has_perm = True

        return has_perm

    def is_cloud_or_client_super_admin(self):
        return self.is_cloud_super_admin() or self.is_client_super_admin()

    def is_cloud_super_admin(self):
        return self.role_level == RoleLevel.CLOUD_SUPER_ADMIN

    def is_client_super_admin(self):
        return self.role_level == RoleLevel.CLIENT_SUPER_ADMIN

    def is_normal_admin(self):
        return self.role_level == RoleLevel.ADMIN
