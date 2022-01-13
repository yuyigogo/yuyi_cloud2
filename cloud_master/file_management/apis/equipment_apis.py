import logging

from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.services.equipment_service import EquipmentService
from file_management.validators.equipment_serializers import (
    CreateEquipmentSerializer,
    DeleteEquipmentSerializer,
    UpdateEquipmentSerializer,
)
from mongoengine import DoesNotExist
from rest_framework.status import HTTP_201_CREATED

from common.const import RoleLevel
from common.framework.exception import APIException
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class EquipmentListView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("POST",),
        ),
    )

    def post(self, request, site_id):
        """ create a new equipment for site"""
        user = request.user
        data, _ = self.get_validated_data(CreateEquipmentSerializer, site_id=site_id)
        logger.info(f"{user.username} request create a new equipment with data")
        equipment = EquipmentService(site_id).create_new_equipment(data)
        return BaseResponse(data=equipment.to_dict(), status_code=HTTP_201_CREATED)

    def get(self, request, site_id):
        """get list equipments in one site"""
        equipments = EquipmentService(site_id).get_equipments_for_site()
        return BaseResponse(data=equipments)


class EquipmentView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("DELETE", "PUT"),
        ),
    )

    @staticmethod
    def _get_equipment(equipment_id):
        try:
            equipment = ElectricalEquipment.objects.get(pk=equipment_id)
        except DoesNotExist:
            raise APIException("invalid equipment_id!")
        return equipment

    def get(self, request, site_id, equipment_id):
        equipment = self._get_equipment(equipment_id)
        return BaseResponse(data=equipment.to_dict())

    def put(self, request, site_id, equipment_id):
        user = request.user
        data, _ = self.get_validated_data(
            UpdateEquipmentSerializer, site_id=site_id, equipment_id=equipment_id
        )
        logger.info(f"{user.username} request update equipment with {data=}")
        device_name = data.get("device_name")
        device_type = data.get("device_type")
        remarks = data.get("remarks")
        voltage_level = data.get("voltage_level")
        operation_number = data.get("operation_number")
        asset_number = data.get("asset_number")
        device_model = data.get("device_model")
        factory_number = data.get("factory_number")
        equipment = self._get_equipment(equipment_id)

        update_fields = {}
        if device_name:
            update_fields["device_name"] = device_name
        if device_type:
            update_fields["device_type"] = device_type
        if remarks:
            update_fields["remarks"] = remarks
        if voltage_level:
            update_fields["voltage_level"] = voltage_level
        if operation_number:
            update_fields["operation_number"] = operation_number
        if asset_number:
            update_fields["asset_number"] = asset_number
        if device_model:
            update_fields["device_model"] = device_model
        if factory_number:
            update_fields["factory_number"] = factory_number
        if update_fields:
            equipment.update(**update_fields)
        return BaseResponse(data=update_fields)

    def delete(self, request, site_id, equipment_id):
        user = request.user
        data, _ = self.get_validated_data(DeleteEquipmentSerializer)
        logger.info(f"{user.username} request delete {equipment_id=} in {site_id=}")
        clear_resource = data["clear_resource"]
        EquipmentService.delete_equipment(equipment_id, clear_resource=clear_resource)
        return BaseResponse()
