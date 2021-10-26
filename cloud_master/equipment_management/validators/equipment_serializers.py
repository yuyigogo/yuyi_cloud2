from mongoengine import DoesNotExist
from rest_framework.fields import CharField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.framework.exception import InvalidException
from common.framework.serializer import BaseSerializer
from sites.models.site import Site


class CreateEquipmentSerializer(BaseSerializer):
    device_name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    device_type = CharField(required=True)
    voltage_level = CharField(required=True)
    operation_number = CharField()
    asset_number = CharField()
    device_model = CharField()
    factory_number = CharField()
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)

    def validate(self, data: dict) -> dict:
        site_id = self.context["site_id"]
        try:
            site = Site.objects.get(id=site_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {site_id=}")
        return data
