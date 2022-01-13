import logging

from customer.models.customer import Customer
from file_management.models.electrical_equipment import ElectricalEquipment
from mongoengine import DoesNotExist
from navigation.services.equipment_navigation_service import SiteNavigationService
from rest_framework.status import HTTP_404_NOT_FOUND
from sites.models.site import Site

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomerTreesView(BaseView):
    def get(self, request):
        """
        设备/测点树形图
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
            data = list(
                SiteNavigationService.get_one_customer_tree_infos(customer, add_point)
            )
        return BaseResponse(data=data)


class SiteSensorsView(BaseView):
    def get(self, request, site_id):
        """
        all points(sensors) in the corresponding site；
        站点下所有最新一条传感器的数据详情
        :param site_id:
        :return:
        """
        try:
            site = Site.objects.get(id=site_id)
        except DoesNotExist:
            logger.info(f"invalid {site_id=}")
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        site_sensors = SiteNavigationService.get_all_sensors_in_site(site)
        return BaseResponse(data=site_sensors)


class EquipmentSensorsView(BaseView):
    def get(self, request, equipment_id):
        """
        all points(sensors) in the corresponding equipment；
        设备下所有最新一条传感器的数据
        :param equipment_id:
        :return:
        """
        try:
            equipment = ElectricalEquipment.objects.get(id=equipment_id)
        except DoesNotExist:
            logger.info(f"invalid {equipment_id=}")
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        equipment_sensors = SiteNavigationService.get_all_sensors_in_equipment(
            equipment
        )
        return BaseResponse(data=equipment_sensors)


class CustomerSensorsView(BaseView):
    def get(self, request, customer_id):
        """
        all points(sensors) in the corresponding customer；
        公司下所有最新一条传感器的数据(暂时没用，最大粒度在站点)
        :param request:
        :param customer_id:
        :return:
        """
        # todo validate user has permissions or not.
        try:
            customer = Customer.objects.get(id=customer_id)
        except DoesNotExist:
            logger.info(f"invalid {customer_id=}")
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        customer_sensors = SiteNavigationService.get_all_sensors_in_customer(customer)
        return BaseResponse(data=customer_sensors)
