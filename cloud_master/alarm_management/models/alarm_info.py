from cloud.models import CloudDocument
from mongoengine import BooleanField, IntField, ObjectIdField, StringField

from common.const import MAX_MESSAGE_LENGTH


class AlarmInfo(CloudDocument):
    sensor_id = StringField(required=True)
    sensor_type = StringField(required=True)
    alarm_type = IntField(required=True)
    alarm_level = IntField(required=True)
    alarm_describe = StringField(max_length=MAX_MESSAGE_LENGTH)
    is_processed = BooleanField(default=False)
    is_online = BooleanField(default=True)
    is_latest = BooleanField(default=True)
    sensor_data_id = ObjectIdField()
    client_number = StringField(required=True)
    # todo get sensor_info from redis
    site_id = ObjectIdField()
    equipment_id = ObjectIdField()
    measure_point_id = ObjectIdField()
    measure_name = StringField()
    device_name = StringField()

    meta = {
        "indexes": [
            "sensor_id",
            "alarm_type",
            "alarm_level",
            "sensor_type",
            "is_latest",
        ],
        "index_background": True,
        "collection": "alarm_info",
    }

    def __str__(self):
        return "AlarmInfo: {}".format(self.sensor_id)

    def __repr__(self):
        return self.__str__()
