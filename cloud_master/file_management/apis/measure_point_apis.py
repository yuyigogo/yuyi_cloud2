import logging

from file_management.services.meansure_point_service import MeasurePointService
from file_management.validators.measure_point_serializers import \
    CreatePointSerializer
from rest_framework.status import HTTP_201_CREATED

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class MeasurePointListView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("POST",),
        ),
    )

    def post(self, request, equipment_id):
        """ create a new measure point for equipment"""
        user = request.user
        data, _ = self.get_validated_data(
            CreatePointSerializer, equipment_id=equipment_id
        )
        logger.info(f"{user.username} request create a new measure point with data")
        measure_point = MeasurePointService(equipment_id).create_new_measure_point(data)
        return BaseResponse(data=measure_point.to_dict(), status_code=HTTP_201_CREATED)

    def get(self, request, equipment_id):
        """get list points in one equipment"""
        points = MeasurePointService(equipment_id).get_points_for_equipment()
        return BaseResponse(data=points)
