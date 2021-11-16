from mongoengine import DoesNotExist
from rest_framework.status import HTTP_404_NOT_FOUND

from common.framework.response import BaseResponse
from common.framework.view import BaseView
from file_management.models.electrical_equipment import ElectricalEquipment
from navigation.services.equipment_navigation_service import SiteNavigationService


class EquipmentsNavigationView(BaseView):
    def get(self, site_id):
        """
        all points(sensors) in the corresponding site
        :param site_id:
        :return:
        """
        pass


class EquipmentNavigationView(BaseView):
    def get(self, site_id, equipment_id):
        """
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
