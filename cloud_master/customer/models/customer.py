from cloud.models import CloudDocument
from mongoengine import StringField, DictField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH


class Customer(CloudDocument):
    name = StringField(unique=True, max_length=MAX_LENGTH_NAME)
    administrative_division = DictField(required=True)
    remarks = StringField(max_length=MAX_MESSAGE_LENGTH)

    meta = {"indexes": ["name"], "index_background": True, "collection": "customer"}

    def __str__(self):
        return "CustomerModel: {}".format(self.name)

    def __repr__(self):
        return self.__str__()
