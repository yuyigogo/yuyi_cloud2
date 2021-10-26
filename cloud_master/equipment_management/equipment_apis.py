import logging

from rest_framework.status import HTTP_201_CREATED

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView
from equipment_management.services.equipment_service import EquipmentService
from equipment_management.validators.equipment_serializers import (
    CreateEquipmentSerializer,
)

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
