from datetime import datetime

import pytz

from cloud.models import CloudDocument
from mongoengine import ListField, ObjectIdField, StringField, DateTimeField, IntField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH


class Sensor(CloudDocument):
    name = StringField(unique=True, max_length=MAX_LENGTH_NAME)
    sensor_number = StringField(required=True)
    rtc_set = DateTimeField(default=lambda: datetime.now(tz=pytz.utc))  # time set
    upload_interval = IntField(max_value=172800)  # second
    gain_set = StringField()  # db, 增益选择
    filter_set = StringField()  # 全通 高/低.通
    sensor_type = StringField()
    remarks = StringField(max_length=MAX_MESSAGE_LENGTH)
    gateway_id = ObjectIdField(required=True)

    meta = {
        "indexes": ["name", "sensor_number", "sensor_type", "gateway_id"],
        "index_background": True,
        "collection": "sensor",
    }

    def __str__(self):
        return "Sensor: {}".format(self.name)

    def __repr__(self):
        return self.__str__()
