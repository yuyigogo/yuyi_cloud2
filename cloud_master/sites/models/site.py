from cloud.models import CloudDocument
from mongoengine import IntField, ListField, ObjectIdField, StringField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH


class Site(CloudDocument):
    name = StringField(unique=True, max_length=MAX_LENGTH_NAME)
    administrative_division = StringField(required=True)
    voltage_level = IntField(required=True)
    site_location = ListField()
    remarks = StringField(max_length=MAX_MESSAGE_LENGTH)
    customer = ObjectIdField(required=True)

    meta = {
        "indexes": ["name", "customer"],
        "index_background": True,
        "collection": "site",
    }

    def __str__(self):
        return "SiteModel: {}".format(self.name)

    def __repr__(self):
        return self.__str__()
