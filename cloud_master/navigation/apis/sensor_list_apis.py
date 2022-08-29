import logging
from typing import Optional

from file_management.models.electrical_equipment import ElectricalEquipment
from navigation.services.sensor_list_service import SensorListService
from navigation.validators.sensor_list_sereializers import (
    SensorDetailsSerializer,
    SensorListSerializer,
)
from rest_framework.status import HTTP_404_NOT_FOUND
from sites.models.site import Site

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class SensorsBaseView(BaseView):
    @classmethod
    def validate_site_or_equipment(
        cls, site_id: Optional[str] = None, equipment_id: Optional[str] = None
    ) -> int:
        assert (
            site_id or equipment_id
        ), "should have one value in site_id or equipment_id "
        if site_id:
            return Site.objects(id=site_id).count()
        else:
            return ElectricalEquipment.objects(id=equipment_id).count()

    @classmethod
    def _get_sensor_list_from_site_or_equipment(
        cls,
        data: dict,
        site_id: Optional[str] = None,
        equipment_id: Optional[str] = None,
    ) -> tuple:
        page = data.get("page", 1)
        limit = data.get("limit", 10)
        point_id = data.get("point_id")
        alarm_level = data.get("alarm_level")
        is_online = data.get("is_online")
        sensor_type = data.get("sensor_type")
        total, data = SensorListService.get_sensor_list_from_site_or_equipment(
            page,
            limit,
            site_id=site_id,
            equipment_id=equipment_id,
            point_id=point_id,
            alarm_level=alarm_level,
            is_online=is_online,
            sensor_type=sensor_type,
        )
        return total, data


class SiteSensorsView(SensorsBaseView):
    def get(self, request, site_id):
        """
        all points(sensors) in the corresponding site；
        站点下所有最新一条传感器的数据详情
        :param site_id:
        :return:
        """
        data, _ = self.get_validated_data(SensorListSerializer)
        if not self.validate_site_or_equipment(site_id=site_id):
            logger.info(f"invalid {site_id=}")
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        logger.info(f"{request.user.username} request list sensors in {site_id=}")
        total, site_sensor_infos = self._get_sensor_list_from_site_or_equipment(
            data, site_id=site_id
        )
        return BaseResponse(data={"sensor_list": site_sensor_infos, "total": total})


class EquipmentSensorsView(SensorsBaseView):
    def get(self, request, equipment_id):
        """
        all points(sensors) in the corresponding equipment；
        设备下所有最新一条传感器的数据
        :param equipment_id:
        :return:
        """
        data, _ = self.get_validated_data(SensorListSerializer)
        if not self.validate_site_or_equipment(equipment_id=equipment_id):
            logger.info(f"invalid {equipment_id=}")
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        total, equipment_sensor_infos = self._get_sensor_list_from_site_or_equipment(
            data, equipment_id=equipment_id
        )
        return BaseResponse(
            data={"sensor_list": equipment_sensor_infos, "total": total}
        )


class CustomerSensorsView(BaseView):
    def get(self, request, customer_id):
        """
        all points(sensors) in the corresponding customer；
        公司下所有最新一条传感器的数据(暂时没用，最大粒度在站点)
        :param request:
        :param customer_id:
        :return:
        """
        # try:
        #     customer = Customer.objects.get(id=customer_id)
        # except DoesNotExist:
        #     logger.info(f"invalid {customer_id=}")
        #     return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        # customer_sensors = SiteNavigationService.get_all_sensors_in_customer(customer)
        # return BaseResponse(data=customer_sensors)
        pass


class SensorDetailsView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            RoleLevel.ADMIN.value,
        ),
    )

    def get(self, request, pk, sensor_type):
        _, context = self.get_validated_data(
            SensorDetailsSerializer, pk=pk, sensor_type=sensor_type
        )
        logger.info(
            f"{request.user.username} request sensor details for {pk=}, {sensor_type=}"
        )
        sensor_obj_dict = context["sensor_obj_dict"]
        return BaseResponse(data=sensor_obj_dict)
