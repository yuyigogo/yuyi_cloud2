from cloud.models import CloudDocument
from mongoengine import DictField, ListField, ObjectIdField, StringField


class CStatusStatistic(CloudDocument):
    customer_id = ObjectIdField(required=True)
    asset_info = DictField()
    equipment_status_info = ListField()
    sensor_online_ratio = ListField()
    point_distribution_info = ListField()

    meta = {
        "indexes": ["customer_id"],
        "index_background": True,
        "collection": "c_status_statistic",
    }

    def __str__(self):
        return "CStatusStatistic: {}".format(self.customer_id)

    def __repr__(self):
        return self.__str__()


class SStatusStatistic(CloudDocument):
    site_id = ObjectIdField(required=True)
    asset_info = DictField()
    equipment_status_info = ListField()
    sensor_online_ratio = StringField()
    point_distribution_info = ListField()

    meta = {
        "indexes": ["site_id"],
        "index_background": True,
        "collection": "s_status_statistic",
    }

    def __str__(self):
        return "SStatusStatistic: {}".format(self.site_id)

    def __repr__(self):
        return self.__str__()


class CAbnormalRatio(CloudDocument):
    customer_id = ObjectIdField(required=True)
    c_ratio = StringField()

    meta = {
        "indexes": ["customer_id"],
        "index_background": True,
        "collection": "c_abnormal_ratio",
    }


class SAbnormalRatio(CloudDocument):
    site_id = ObjectIdField(required=True)
    s_ratio = StringField()

    meta = {
        "indexes": ["site_id"],
        "index_background": True,
        "collection": "s_abnormal_ratio",
    }
