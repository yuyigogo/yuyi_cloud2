from mongoengine import DoesNotExist
from rest_framework.fields import CharField, IntegerField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.framework.exception import InvalidException
from common.framework.serializer import BaseSerializer
from sites.models.site import Site


class CreateGatewaySerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    customer = CharField(required=True)
    client_number = CharField(required=True)
    time_adjusting = IntegerField(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)

    def validate(self, data: dict) -> dict:
        site_id = self.context["site_id"]
        try:
            site = Site.objects.get(id=site_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {site_id=}")
        return data
