import logging

from file_management.models.measure_point import MeasurePoint
from file_management.services.meansure_point_service import MeasurePointService
from file_management.validators.measure_point_serializers import (
    CreatePointSerializer,
    UpdatePointSerializer,
    DeletePointSerializer,
)
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


class MeasurePointView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("PUT", "DELETE"),
        ),
    )

    def get(self, request, equipment_id, point_id):
        point = MeasurePoint.objects.get(equipment_id=equipment_id, id=point_id)
        return BaseResponse(data=point.to_dict())

    def put(self, request, equipment_id, point_id):
        user = request.user
        data, context = self.get_validated_data(
            UpdatePointSerializer, equipment_id=equipment_id, point_id=point_id
        )
        logger.info(f"{user.username} request update point with {data=}")
        measure_name = data.get("measure_name")
        measure_type = data.get("measure_type")
        sensor_number = data.get("sensor_number")
        remarks = data.get("remarks")
        point = context["point"]
        update_fields = {}
        if measure_name:
            update_fields["measure_name"] = measure_name
        if measure_type:
            update_fields["measure_name"] = measure_name
        if sensor_number:
            update_fields["sensor_number"] = sensor_number
        if remarks:
            update_fields["remarks"] = remarks
        if update_fields:
            point.update(**update_fields)
        return BaseResponse(data=update_fields)

    def delete(self, request, equipment_id, point_id):
        user = request.user
        data, _ = self.get_validated_data(DeletePointSerializer)
        logger.info(f"{user.username} request delete point: {point_id} with {data=}")
        MeasurePointService.delete_point(point_id)
        return BaseResponse()
