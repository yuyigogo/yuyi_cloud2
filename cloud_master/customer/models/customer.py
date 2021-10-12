from cloud.models import CloudDocument
from mongoengine import StringField


class Customer(CloudDocument):
    name = StringField(unique=True)
    administrative_division = StringField(required=True)
    remarks = StringField(max_length=2000)

    meta = {"indexes": ["name"], "index_background": True, "collection": "customer"}

    def __str__(self):
        return "CustomerModel: {}".format(self.name)

    def __repr__(self):
        return self.__str__()
