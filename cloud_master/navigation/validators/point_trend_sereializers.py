from rest_framework.fields import CharField, ListField, RegexField

from common.framework.serializer import BaseSerializer


class BasePointSerializer(BaseSerializer):
    point_ids = ListField(child=RegexField(r"^[0-9a-fA-F]{24}$"), required=True)
    start_date = CharField(required=True)


class PointTrendSerializer(BasePointSerializer):
    end_date = CharField(required=True)
