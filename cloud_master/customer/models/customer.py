from cloud.models import CloudDocument
from mongoengine import StringField

from common.const import MAX_MESSAGE_LENGTH


class Customer(CloudDocument):
    name = StringField(unique=True)
    administrative_division = StringField(required=True)
    remarks = StringField(max_length=MAX_MESSAGE_LENGTH)

    meta = {"indexes": ["name"], "index_background": True, "collection": "customer"}

    def __str__(self):
        return "CustomerModel: {}".format(self.name)

    def __repr__(self):
        return self.__str__()
