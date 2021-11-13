from cloud.models import CloudDocument
from mongoengine import ObjectIdField, StringField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH


class MeasurePoint(CloudDocument):
    measure_name = StringField(required=True, max_length=MAX_LENGTH_NAME)
    measure_type = StringField(required=True, max_length=MAX_LENGTH_NAME)
    sensor_number = StringField(required=True)
    remarks = StringField(max_length=MAX_MESSAGE_LENGTH)
    equipment_id = ObjectIdField()

    meta = {
        "indexes": ["sensor_number", "equipment_id"],
        "index_background": True,
        "collection": "measure_point",
    }

    def __str__(self):
        return "MeasurePoint: {}".format(self.measure_name)

    def __repr__(self):
        return self.__str__()