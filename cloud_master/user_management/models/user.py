from mongoengine import StringField, ObjectIdField, ReferenceField, EmailField, BinaryField, IntField

from models import DocumentMixin
from user_management.models.user_session import UserSession
from vendor.django_mongoengine.mongo_auth.models import User
from vendor.django_mongoengine.sessions import MongoSession


class CloudUser(User, DocumentMixin):
    password = StringField(required=True, max_length=128)
    username = StringField(max_length=100, required=True, verbose_name="username")
    customer = ObjectIdField(required=True)
    phone = StringField(max_length=50)
    email = EmailField(required=True, unique=True, max_length=100)
    avatar = BinaryField()
    role_level = IntField(required=True)
    # permissions_profile = ReferenceField(PermissionsProfile)

    meta = {
        "indexes": [
            "customer",
            "email",
        ],
        "index_background": True,
    }

    def remove_sessions(self):
        user_sessions = UserSession.objects(user_id=self.id)
        for user_session in user_sessions:
            try:
                MongoSession.objects.get(session_key=user_session.session_key).delete()
            except:
                pass
            user_session.delete()
