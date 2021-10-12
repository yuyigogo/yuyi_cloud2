from cloud.models import CloudDocument
from mongoengine import IntField, ListField, StringField


class Site(CloudDocument):
    name = StringField(unique=True)
    administrative_division = StringField(required=True)
    voltage_level = IntField(required=True)
    site_location = ListField()
    remarks = StringField(max_length=2000)

    meta = {"indexes": ["name"], "index_background": True, "collection": "site"}

    def __str__(self):
        return "SiteModel: {}".format(self.name)

    def __repr__(self):
        return self.__str__()
