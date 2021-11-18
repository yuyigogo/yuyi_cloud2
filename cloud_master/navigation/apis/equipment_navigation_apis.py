from file_management.models.electrical_equipment import ElectricalEquipment
from mongoengine import DoesNotExist
from navigation.services.equipment_navigation_service import SiteNavigationService
from rest_framework.status import HTTP_404_NOT_FOUND

from common.framework.response import BaseResponse
from common.framework.view import BaseView


class EquipmentsNavigationView(BaseView):
    def get(self, request, site_id):
        """
        某个站点下所有设备对应的测点(传感器)数据列表
        all points(sensors) in the corresponding site
        :param site_id:
        :return:
        """
        equipments = ElectricalEquipment.objects.only(
            "device_name", "device_type"
        ).filter(site_id=site_id)
        data = SiteNavigationService.get_all_points_in_site(equipments)
        return BaseResponse(data=data)


class EquipmentNavigationView(BaseView):
    def get(self, request, site_id, equipment_id):
        """
        设备下所有测点(传感器)数据列表
        all points(sensors) in the corresponding equipment
        :param site_id:
        :param equipment_id:
        :return:
        """
        try:
            equipment = ElectricalEquipment.objects.get(id=equipment_id)
        except DoesNotExist:
            return BaseResponse(status_code=HTTP_404_NOT_FOUND)
        points = SiteNavigationService.get_all_points_in_equipment(equipment)
        return BaseResponse(data=points)
