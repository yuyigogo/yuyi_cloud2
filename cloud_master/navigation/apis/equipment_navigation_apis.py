import logging
from typing import Optional

from customer.models.customer import Customer
from file_management.models.electrical_equipment import ElectricalEquipment
from navigation.services.equipment_navigation_service import SiteNavigationService
from navigation.services.sensor_list_service import SensorListService
from navigation.validators.sensor_list_sereializers import SensorListSerializer
from rest_framework.status import HTTP_404_NOT_FOUND
from sites.models.site import Site

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomerTreesView(BaseView):
    def get(self, request):
        """
        公司树形图
        :param request:
        :return:
        """
        user = request.user
        customer_id = user.customer
        add_point = bool(request.GET.get("add_point", 0))
        logger.info(
            f"{user.username} request CustomerTrees with {add_point=} for {customer_id=}"
        )
        if user.is_cloud_or_client_super_admin():
            # get all customer tree infos
            data = SiteNavigationService.get_customers_tree_infos(
                customer_id, add_point
            )
        else:
            # get corresponding customer's tree info
            customer = Customer.objects.only("name").get(pk=customer_id)
            query_sites = user.sites if user.is_normal_admin() else None
            data = [
                SiteNavigationService.get_one_customer_tree_infos(
                    customer, add_point, site_ids=query_sites
                )
            ]
        return BaseResponse(data=data)


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
