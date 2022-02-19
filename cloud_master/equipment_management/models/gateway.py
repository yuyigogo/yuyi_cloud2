from datetime import datetime

import pytz

from cloud.models import CloudDocument
from mongoengine import ObjectIdField, StringField, DateTimeField, ListField, DictField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH


class GateWay(CloudDocument):
    name = StringField(unique=True, max_length=MAX_LENGTH_NAME)
    client_number = StringField(required=True)
    site_id = ObjectIdField(required=True)
    customer = ObjectIdField(required=True)
    time_adjusting = DateTimeField(default=lambda: datetime.now(tz=pytz.utc))
    remarks = StringField(max_length=MAX_MESSAGE_LENGTH)
    sensor_info = DictField()  # {"sensor_ids": [], "sensor_types": []}

    meta = {
        "indexes": ["name", "customer", "site_id"],
        "index_background": True,
        "collection": "gateway",
    }

    def __str__(self):
        return "GateWay: {}".format(self.name)

    def __repr__(self):
        return self.__str__()
