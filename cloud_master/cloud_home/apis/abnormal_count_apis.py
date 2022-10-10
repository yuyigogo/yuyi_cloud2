from common.const import (
    customer_day_abnormal_info,
    customer_month_abnormal_info,
    customer_week_abnormal_info,
    site_day_abnormal_info,
    site_month_abnormal_info,
    site_week_abnormal_info,
)
from common.framework.response import BaseResponse
from common.framework.view import BaseView
from common.storage.redis import redis
"""
1. hincrby:
    subscribe_message: hincrby: alarm_num;
    when processed/unprocessed a alarm: hincrby: processed_num;
2. expire time
3. ws
"""


class CustomerAbnormalCountView(BaseView):
    def get(self, request, customer_id):
        customer_day_abnormal_key = f"{customer_day_abnormal_info}{customer_id}"
        customer_week_abnormal_key = f"{customer_week_abnormal_info}{customer_id}"
        customer_month_abnormal_key = f"{customer_month_abnormal_info}{customer_id}"
        data = {
            "customer_day_abnormal_info": redis.hgetall(customer_day_abnormal_key),
            "customer_week_abnormal_info": redis.hgetall(customer_week_abnormal_key),
            "customer_month_abnormal_info": redis.hgetall(customer_month_abnormal_key),
        }
        return BaseResponse(data=data)


class SiteAbnormalCountView(BaseView):
    def get(self, request, site_id):
        site_day_abnormal_key = f"{site_day_abnormal_info}{site_id}"
        site_week_abnormal_key = f"{site_week_abnormal_info}{site_id}"
        site_month_abnormal_key = f"{site_month_abnormal_info}{site_id}"
        data = {
            "site_day_abnormal_info": redis.hgetall(site_day_abnormal_key),
            "site_week_abnormal_info": redis.hgetall(site_week_abnormal_key),
            "site_month_abnormal_info": redis.hgetall(site_month_abnormal_key),
        }
        return BaseResponse(data=data)
