import calendar
import datetime
from functools import lru_cache

from customer.models.customer import Customer

from common.const import (
    ALL,
    customer_day_abnormal_info,
    customer_month_abnormal_info,
    customer_week_abnormal_info,
    site_day_abnormal_info,
    site_month_abnormal_info,
    site_week_abnormal_info,
)
from common.framework.service import BaseService
from common.storage.redis import normal_redis


class AbnormalCacheService(BaseService):
    """
    this service is for creating or updating day/week/month abnormal info for customer/site.
    1. hincrby:
    subscribe_message: hincrby: alarm_num;
    when processed/unprocessed a alarm: hincrby: processed_num;
    2. expire time
    3. ws
    """

    ALARM_NUM = "alarm_num"
    PROCESSED_NUM = "processed_num"

    def __init__(self, customer_id: str, site_id: str):
        self.customer_id = customer_id
        self.site_id = site_id
        self.customer_day_abnormal_info_key = (
            f"{customer_day_abnormal_info}{customer_id}"
        )
        self.customer_week_abnormal_info_key = (
            f"{customer_week_abnormal_info}{customer_id}"
        )
        self.customer_month_abnormal_info_key = (
            f"{customer_month_abnormal_info}{customer_id}"
        )

        self.site_day_abnormal_info_key = f"{site_day_abnormal_info}{site_id}"
        self.site_week_abnormal_info_key = f"{site_week_abnormal_info}{site_id}"
        self.site_month_abnormal_info_key = f"{site_month_abnormal_info}{site_id}"

    @classmethod
    @lru_cache
    def get_named_all_customer_id(cls):
        return str(Customer.objects.get(name=ALL).pk)

    @property
    def named_all_customer_day_abnormal_info_key(self):
        return f"{customer_day_abnormal_info}{self.get_named_all_customer_id()}"

    @property
    def named_all_customer_week_abnormal_info_key(self):
        return f"{customer_week_abnormal_info}{self.get_named_all_customer_id()}"

    @property
    def named_all_customer_month_abnormal_info_key(self):
        return f"{customer_month_abnormal_info}{self.get_named_all_customer_id()}"

    def auto_increment_customer_abnormal_infos(self, is_alarm_num=True, amount=1):
        """
        increment or decrement customer's abnormal infos;
        is_alarm_num: bool, if true, means deal with alarm_num key, else is processed_num key
        amount: int, increment/decrement number
        """
        updated_key = self.ALARM_NUM if is_alarm_num else self.PROCESSED_NUM
        # customer day info
        if normal_redis.exists(self.customer_day_abnormal_info_key):
            normal_redis.hincrby(self.customer_day_abnormal_info_key, updated_key, amount)
            normal_redis.hincrby(
                self.named_all_customer_day_abnormal_info_key, updated_key, amount
            )
        else:
            now = datetime.datetime.now()
            zero_today = now - datetime.timedelta(
                hours=now.hour,
                minutes=now.minute,
                seconds=now.second,
                microseconds=now.microsecond,
            )
            expire_time = zero_today + datetime.timedelta(seconds=86400)
            # set value
            normal_redis.hset(
                self.customer_day_abnormal_info_key, key=updated_key, value=amount
            )
            normal_redis.hset(
                self.named_all_customer_day_abnormal_info_key,
                key=updated_key,
                value=amount,
            )
            # set expire time
            normal_redis.expireat(self.customer_day_abnormal_info_key, expire_time)
            normal_redis.expireat(self.named_all_customer_day_abnormal_info_key, expire_time)
        # customer week info
        if normal_redis.exists(self.customer_week_abnormal_info_key):
            normal_redis.hincrby(self.customer_week_abnormal_info_key, updated_key, amount)
            normal_redis.hincrby(
                self.named_all_customer_week_abnormal_info_key, updated_key, amount
            )
        else:
            now = datetime.datetime.now()
            zero_today = now - datetime.timedelta(
                hours=now.hour,
                minutes=now.minute,
                seconds=now.second,
                microseconds=now.microsecond,
            )
            interval_days = 7 - now.isoweekday() + 1
            expire_time = zero_today + datetime.timedelta(days=interval_days)
            # set value
            normal_redis.hset(
                self.customer_week_abnormal_info_key, key=updated_key, value=amount
            )
            normal_redis.hset(
                self.named_all_customer_week_abnormal_info_key,
                key=updated_key,
                value=amount,
            )
            # set expire time
            normal_redis.expireat(self.customer_week_abnormal_info_key, expire_time)
            normal_redis.expireat(self.named_all_customer_week_abnormal_info_key, expire_time)
            # customer month info
            if normal_redis.exists(self.customer_month_abnormal_info_key):
                normal_redis.hincrby(
                    self.customer_month_abnormal_info_key, updated_key, amount
                )
                normal_redis.hincrby(
                    self.named_all_customer_month_abnormal_info_key, updated_key, amount
                )
            else:
                now = datetime.datetime.now()
                zero_today = now - datetime.timedelta(
                    hours=now.hour,
                    minutes=now.minute,
                    seconds=now.second,
                    microseconds=now.microsecond,
                )
                _, total_days = calendar.monthrange(now.year, now.month)
                interval_days = total_days - now.day + 1
                expire_time = zero_today + datetime.timedelta(days=interval_days)
                # set value
                normal_redis.hset(
                    self.customer_month_abnormal_info_key, key=updated_key, value=amount
                )
                normal_redis.hset(
                    self.named_all_customer_month_abnormal_info_key,
                    key=updated_key,
                    value=amount,
                )
                # set expire time
                normal_redis.expireat(self.customer_month_abnormal_info_key, expire_time)
                normal_redis.expireat(
                    self.named_all_customer_month_abnormal_info_key, expire_time
                )

    def auto_increment_site_abnormal_infos(self, is_alarm_num=True, amount=1):
        updated_key = self.ALARM_NUM if is_alarm_num else self.PROCESSED_NUM
        # site day info
        if normal_redis.exists(self.site_day_abnormal_info_key):
            normal_redis.hincrby(self.site_day_abnormal_info_key, updated_key, amount)
        else:
            now = datetime.datetime.now()
            zero_today = now - datetime.timedelta(
                hours=now.hour,
                minutes=now.minute,
                seconds=now.second,
                microseconds=now.microsecond,
            )
            expire_time = zero_today + datetime.timedelta(seconds=86400)
            # set value
            normal_redis.hset(self.site_day_abnormal_info_key, key=updated_key, value=amount)
            # set expire time
            normal_redis.expireat(self.site_day_abnormal_info_key, expire_time)
        # site week info
        if normal_redis.exists(self.site_week_abnormal_info_key):
            normal_redis.hincrby(self.site_week_abnormal_info_key, updated_key, amount)
        else:
            now = datetime.datetime.now()
            zero_today = now - datetime.timedelta(
                hours=now.hour,
                minutes=now.minute,
                seconds=now.second,
                microseconds=now.microsecond,
            )
            interval_days = 7 - now.isoweekday() + 1
            expire_time = zero_today + datetime.timedelta(days=interval_days)
            # set value
            normal_redis.hset(self.site_week_abnormal_info_key, key=updated_key, value=amount)
            # set expire time
            normal_redis.expireat(self.site_week_abnormal_info_key, expire_time)
            # site month info
            if normal_redis.exists(self.site_month_abnormal_info_key):
                normal_redis.hincrby(self.site_month_abnormal_info_key, updated_key, amount)
            else:
                now = datetime.datetime.now()
                zero_today = now - datetime.timedelta(
                    hours=now.hour,
                    minutes=now.minute,
                    seconds=now.second,
                    microseconds=now.microsecond,
                )
                _, total_days = calendar.monthrange(now.year, now.month)
                interval_days = total_days - now.day + 1
                expire_time = zero_today + datetime.timedelta(days=interval_days)
                # set value
                normal_redis.hset(
                    self.site_month_abnormal_info_key, key=updated_key, value=amount
                )
                # set expire time
                normal_redis.expireat(self.site_month_abnormal_info_key, expire_time)
