from cloud.models import CloudDocument
from mongoengine import IntField, ObjectIdField, StringField


class SensorConfig(CloudDocument):
    """
    1. create this model when create measure_point;
    2. set model_key, client_number, can_senor_online, communication_mode fields when get sensor_list from
        gateway;
    3. delete this model when customer/site/point deleted
    """

    sensor_number = StringField(required=True)
    sensor_type = StringField()
    client_number = StringField()
    model_key = StringField()
    can_senor_online = IntField(default=0)  # 是否支持在线模式, 0:不支持， 1：支持
    communication_mode = StringField()
    # rtc_set = DateTimeField(default=lambda: datetime.now(tz=pytz.utc))  # time set
    # gain_set = StringField()  # db, 增益选择
    # filter_set = StringField()  # 全通 高/低.通
    customer_id = ObjectIdField()
    site_id = ObjectIdField()
    equipment_id = ObjectIdField()
    point_id = ObjectIdField()

    meta = {
        "indexes": ["sensor_number", "client_number", "sensor_type", "site_id"],
        "index_background": True,
        "collection": "sensor_config",
    }

    def __str__(self):
        return "SensorConfig: {}-{}".format(self.sensor_number, self.sensor_type)

    def __repr__(self):
        return self.__str__()
