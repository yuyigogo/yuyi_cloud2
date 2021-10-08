import binascii
import datetime
import os

from django.conf import settings
from mongoengine import Document, ReferenceField, StringField
from mongoengine.fields import DateTimeField
from user_management.models.user import CloudUser

from common.const import MAX_EXPIRE_DAYS

TOKEN_EXPIRE = getattr(settings, "TOKEN_EXPIRE")


class MongoToken(Document):
    """ Class that manages the access tokens for the system users """

    key = StringField(max_length=44)
    user = ReferenceField(CloudUser, required=True)
    expire = DateTimeField()

    meta = {"indexes": ["key", "user"], "index_background": True}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if not self.key:
            self.key = self.generate_key()
        if not self.expire:
            self.set_expire_date()

    def set_expire_date(self):
        self.expire = datetime.datetime.now() + datetime.timedelta(seconds=TOKEN_EXPIRE)

    def generate_key(self):
        """
        Returns 44 characters string by converting 22 random bytes
        into hex format
        """
        return binascii.hexlify(os.urandom(22)).decode()

    def emit_key(self):
        """ Updates the token with a new key and set the expire date """
        self.set_expire_date()
        self.key = self.generate_key()
        self.save()
        return self.key

    def is_valid(self):
        """ Check if token is valid """
        return datetime.datetime.now() < self.expire

    def is_beyond_max_expire_days(self):
        """check if expired token beyond max expire days"""
        return (datetime.datetime.now() - self.expire) > datetime.timedelta(
            days=MAX_EXPIRE_DAYS
        )

    def __unicode__(self):
        return self.key
