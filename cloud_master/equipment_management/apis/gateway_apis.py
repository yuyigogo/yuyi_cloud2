import logging

from equipment_management.models.gateway import GateWay
from equipment_management.services.gateway_services import GatewayService
from equipment_management.validators.gateway_serializers import (
    CreateGatewaySerializer,
    UpdateGatewaySerializer,
)
from mongoengine import DoesNotExist
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class GatewaysView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("POST",),
        ),
    )

    def post(self, request, site_id):
        """ create a new gateway"""
        user = request.user
        data, _ = self.get_validated_data(CreateGatewaySerializer, site_id=site_id)
        logger.info(f"{user.username} create a gateway with data: {data}")
        gateway = GatewayService.create_gateway(data, site_id)
        return BaseResponse(data=gateway.to_dict(), status_code=HTTP_201_CREATED)


class GatewayView(BaseView):
    def get(self, request, gateway_id):
        try:
            gateway = GateWay.objects.get(pk=gateway_id)
        except DoesNotExist:
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        return BaseResponse(data=gateway.to_dict())

    def put(self, request, gateway_id):
        user = request.user
        data, _ = self.get_validated_data(
            UpdateGatewaySerializer, gateway_id=gateway_id
        )
        logger.info(f"{user.username} request to put gateway with {data}")
        gateway = data["gateway"]
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
        return BaseResponse(data=update_fields)

    def delete(self, request, gateway_id):
        logger.info(f"{request.user.username} delete a {gateway_id}")
        GateWay.objects.get(pk=gateway_id).delete()
        return BaseResponse()
