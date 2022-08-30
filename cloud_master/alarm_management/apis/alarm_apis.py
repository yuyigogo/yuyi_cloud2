import logging

from alarm_management.services.alarm_list_service import AlarmListService
from alarm_management.validators.alarm_list_sereializers import AlarmListSerializer

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class SiteAlarmListView(BaseView):
    def get(self, request, site_id):
        data, _ = self.get_validated_data(AlarmListSerializer, site_id=site_id)
        logging.info(f"get list alarm infos with {site_id=}, {data=}")
        alarm_type = data["alarm_type"]
        page = data.get("page", 1)
        limit = data.get("limit", 10)
        service = AlarmListService(alarm_type)
        total, data = service.get_alarm_list_from_site_or_equipment(
            page,
            limit,
            site_id=site_id,
            start_date=data.get("start_date"),
            end_date=data.get("start_date"),
            alarm_level=data.get("alarm_level"),
            is_processed=data.get("is_processed"),
            sensor_type=data.get("sensor_type"),
        )
        return BaseResponse(data={"alarm_list": data, "total": total})


class EquipmentAlarmListView(BaseView):
    def get(self, request, equipment_id):
        data, _ = self.get_validated_data(
            AlarmListSerializer, equipment_id=equipment_id
        )
        logging.info(f"get list alarm infos with {equipment_id=}, {data=}")
        alarm_type = data["alarm_type"]
        page = data.get("page", 1)
        limit = data.get("limit", 10)
        service = AlarmListService(alarm_type)
        total, data = service.get_alarm_list_from_site_or_equipment(
            page,
            limit,
            equipment_id=equipment_id,
            start_date=data.get("start_date"),
            end_date=data.get("start_date"),
            alarm_level=data.get("alarm_level"),
            is_processed=data.get("is_processed"),
            sensor_type=data.get("sensor_type"),
        )
        return BaseResponse(data={"alarm_list": data, "total": total})
