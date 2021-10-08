from mongoengine import StringField, ObjectIdField, ReferenceField

from models import DocumentMixin
from vendor.django_mongoengine.mongo_auth.models import User


class CloudUser(User, DocumentMixin):
    password = StringField(required=False, max_length=128)
    username = StringField(max_length=100, required=True, verbose_name="username")
    customer = ObjectIdField()
    phone = StringField(max_length=50)
    # permissions_profile = ReferenceField(PermissionsProfile)
