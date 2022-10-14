import logging

from alarm_management.services.alarm_list_service import AlarmListService
from alarm_management.validators.alarm_list_sereializers import (
    AlarmActionSerializer,
    AlarmListSerializer,
)
from cloud_home.services.abnormal_count_service import AbnormalCacheService

from common.const import SITE_UNPROCESSED_NUM
from common.framework.response import BaseResponse
from common.framework.view import BaseView
from common.storage.redis import normal_redis

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


class AlarmActionView(BaseView):
    def put(self, request, alarm_id):
        data, _ = self.get_validated_data(AlarmActionSerializer, alarm_id=alarm_id)
        logger.info(
            f"{request.user.username} request to update {alarm_id=} with {data=}"
        )
        alarm_info = data["alarm_info"]
        is_processed = data["is_processed"]
        processed_remarks = data.get("processed_remarks", "")
        need_update_in_redis = alarm_info.is_processed != is_processed
        alarm_info.update(
            is_processed=is_processed, processed_remarks=processed_remarks
        )
        # add auto-increment/decrement not processed number
        if need_update_in_redis:
            customer_id = str(alarm_info.customer_id)
            site_id = str(alarm_info.site_id)
            site_unprocessed_key = f"{SITE_UNPROCESSED_NUM}{site_id}"
            if is_processed is True:
                normal_redis.decrby(site_unprocessed_key)
            else:
                normal_redis.incrby(site_unprocessed_key)
            amount = 1 if is_processed else -1
            service = AbnormalCacheService(customer_id, site_id)
            service.auto_increment_customer_abnormal_infos(
                is_alarm_num=False, amount=amount
            )
            service.auto_increment_site_abnormal_infos(
                is_alarm_num=False, amount=amount
            )
        return BaseResponse()
