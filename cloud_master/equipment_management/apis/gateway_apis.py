import logging

from cloud.settings import CLIENT_IDS
from cloud_mqtt.cloud_mqtt_client import cloud_mqtt_client
from cloud_mqtt.sub_pub_topics import BASE_GATEWAY_PUBLISH_TOPIC
from customer.models.customer import Customer
from equipment_management.models.gateway import GateWay
from equipment_management.services.gateway_services import GatewayService
from equipment_management.validators.gateway_serializers import (
    CreateGatewaySerializer,
    DeleteGatewaySerializer,
    UpdateGatewaySerializer,
)
from mongoengine import DoesNotExist
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from sites.models.site import Site

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView
from common.storage.redis import redis

logger = logging.getLogger(__name__)


class GatewaysView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            RoleLevel.ADMIN.value,
        ),
    )

    def get(self, request, site_id):
        # 站点下主机列表信息
        user = request.user
        logger.info(f"{user.username} request list gateways in {site_id=}")
        gateways = GatewayService(site_id).get_list_gateway_in_site()
        return BaseResponse(data=gateways)

    def post(self, request, site_id):
        """ create a new gateway"""
        user = request.user
        data, _ = self.get_validated_data(CreateGatewaySerializer, site_id=site_id)
        logger.info(f"{user.username} create a gateway with data: {data}")
        gateway = GatewayService(site_id).create_gateway(data)
        # add this client_number to redis
        redis.sadd(CLIENT_IDS, gateway.client_number)
        return BaseResponse(data=gateway.to_dict(), status_code=HTTP_201_CREATED)


class GatewayView(BaseView):
    def get(self, request, gateway_id):
        try:
            gateway = GateWay.objects.get(pk=gateway_id)
        except DoesNotExist:
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        customer_name = Customer.objects.get(pk=gateway.customer).name
        site_name = Site.objects.get(id=gateway.site_id).name
        data = {"customer_name": customer_name, "site_name": site_name}
        data.update(gateway.to_dict())
        return BaseResponse(data=data)

    def put(self, request, gateway_id):
        user = request.user
        data, _ = self.get_validated_data(
            UpdateGatewaySerializer, gateway_id=gateway_id
        )
        logger.info(f"{user.username} request to put gateway with {data}")
        gateway = data["gateway"]
        old_client_id = gateway.client_number
        name = data.get("name")
        client_number = data.get("client_number")
        remarks = data.get("remarks")
        update_fields = {}
        if name:
            update_fields["name"] = name
        if client_number:
            update_fields["client_number"] = client_number
        if remarks:
            update_fields["remarks"] = remarks
        if update_fields:
            gateway.update(**update_fields)
        if data["changed_client_id"]:
            redis.srem(CLIENT_IDS, old_client_id)
            redis.sadd(CLIENT_IDS, client_number)
        return BaseResponse(data=update_fields)

    def delete(self, request, gateway_id):
        data, _ = self.get_validated_data(
            DeleteGatewaySerializer, gateway_id=gateway_id
        )
        logger.info(f"{request.user.username} delete a {gateway_id}")
        gateway = data["gateway"]
        clear_resource = data["clear_resource"]
        GatewayService.delete_sensor_data_from_gateway(
            gateway, clear_resource=clear_resource
        )
        return BaseResponse()


class GatewaySensorsView(BaseView):
    def get(self, request, gateway_id):
        pass


class SensorsByPublishView(BaseView):
    def get(self, request, gateway_id):
        client_number = GateWay.objects.get(id=gateway_id).client_number
        logger.info(
            f"{request.user.username} request list sensors in {client_number=} by mqtt publish client"
        )
        topic = f"/8E00000213000265{BASE_GATEWAY_PUBLISH_TOPIC}"
        cloud_mqtt_client.mqtt_publish(topic)
        return BaseResponse()
