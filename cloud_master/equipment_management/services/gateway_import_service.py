import logging
from datetime import datetime
from functools import lru_cache
from typing import Optional

from bson import ObjectId
from cloud.settings import CLIENT_IDS
from customer.models.customer import Customer
from equipment_management.models.gateway import GateWay
from mongoengine import DateTimeField, DoesNotExist, MultipleObjectsReturned
from sites.models.site import Site

from common.framework.exception import APIException
from common.framework.service import BaseService
from common.storage.redis import normal_redis
from common.utils.excel_utils import Workbook

logger = logging.getLogger(__name__)


class GatewayExcelService(BaseService):
    def __init__(self, validate_customer_id: Optional[str]):
        """validate request.user can import this customer from excel"""
        self.validate_customer_id = validate_customer_id
        self.need_validate = True if validate_customer_id else False

    def gateway_file_import(
        self, excel_file=None, excel_file_name=None, sheet_name=None
    ) -> int:
        """
        import gateway data from excel
        :param excel_file: excel file object or excel file contents
        :param excel_file_name: excel file name
        :param sheet_name: excel sheet name
        :return: int: import_succeed_num
        """
        workbook = Workbook.open(excel_file_name=excel_file_name, excel_file=excel_file)
        try:
            workbook_data = list(self.read_workbook_data(workbook, sheet_name))
        except Exception as e:
            logger.exception(f"read excel error with {e=}")
            raise APIException("解析Exel文档错误!")
        return self.save_gateway_import_data(workbook_data)

    @classmethod
    def read_workbook_data(cls, workbook, sheet_name=None):
        for column in workbook.get_columns(
            sheet_name=sheet_name, r_offset=3, c_offset=2
        ):
            result = [value for value in column]
            if any(value.strip() != "" for value in result):
                yield result

    def save_gateway_import_data(self, data_list: list) -> int:
        insert_client_numbers = set()
        bulk_inserts, import_succeed_num = [], 0
        for data in data_list:
            customer_name = data[0]
            site_name = data[1]
            gateway_name = data[2]
            client_number = data[3]
            remarks = data[4]
            if client_number in insert_client_numbers:
                logger.warning(f"{client_number=} has been in one place in excel!")
                continue
            customer_id = self.customer_id(customer_name)
            if not customer_id or (
                self.need_validate and customer_id != self.validate_customer_id
            ):
                logger.warning(
                    f"pop one data from gateway import excel with import customer_id: {customer_id}, "
                    f"{self.validate_customer_id=}"
                )
                continue
            site_id = self.site_id(customer_id, site_name)
            if not site_id:
                continue
            if not self.is_valid_gateway_name(
                site_id, gateway_name
            ) or not self.is_valid_client_number(client_number):
                logger.warning(f"invalid {gateway_name=} or {client_number=}")
                continue
            insert_client_numbers.add(client_number)
            import_succeed_num += 1
            bulk_inserts.append(
                {
                    "name": gateway_name,
                    "client_number": client_number,
                    "customer": ObjectId(customer_id),
                    "site_id": ObjectId(site_id),
                    "remarks": remarks,
                    "create_date": datetime.now(),
                    "update_date": datetime.now(),
                }
            )
        if bulk_inserts:
            collection = GateWay._get_collection()
            collection.insert_many(bulk_inserts, ordered=False)
            v1, *values = insert_client_numbers
            normal_redis.sadd(CLIENT_IDS, v1, *values)
        return import_succeed_num

    @classmethod
    @lru_cache
    def customer_id(cls, customer_name: str) -> Optional[str]:
        try:
            return str(Customer.objects.get(name=customer_name).pk)
        except (DoesNotExist, MultipleObjectsReturned) as e:
            logger.exception(f"can't get customer_id by {customer_name=}")
            return

    @classmethod
    @lru_cache
    def site_id(cls, customer_id: str, site_name: str) -> Optional[str]:
        try:
            return str(Site.objects.get(customer=customer_id, name=site_name).pk)
        except (DoesNotExist, MultipleObjectsReturned) as e:
            logger.exception(f"can't get site_id by {customer_id=}, {site_name=}")
            return

    @classmethod
    def is_valid_gateway_name(cls, site_id: str, gateway_name) -> bool:
        return GateWay.objects.filter(site_id=site_id, name=gateway_name).count() == 0

    @classmethod
    def is_valid_client_number(cls, client_number: str) -> bool:
        return GateWay.objects.filter(client_number=client_number).count() == 0
