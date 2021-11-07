from cloud.models import CloudDocument
from mongoengine import ObjectIdField, StringField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH


class ElectricalEquipment(CloudDocument):
    device_name = StringField(required=True, max_length=MAX_LENGTH_NAME)
    device_type = StringField(required=True, max_length=MAX_LENGTH_NAME)
    voltage_level = StringField(required=True)
    operation_number = StringField()
    asset_number = StringField()
    device_model = StringField()
    factory_number = StringField()
    remarks = StringField(max_length=MAX_MESSAGE_LENGTH)
    site_id = ObjectIdField()

    meta = {
        "indexes": ["site_id"],
        "index_background": True,
        "collection": "electrical_equipment",
    }

    def __str__(self):
        return "ElectricalEquipment: {}".format(self.device_name)

    def __repr__(self):
        return self.__str__()
