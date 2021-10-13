from cloud.models import CloudDocument
from mongoengine import IntField, ListField, StringField, ObjectIdField

from common.const import MAX_MESSAGE_LENGTH


class Site(CloudDocument):
    name = StringField(unique=True)
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
