import logging
from datetime import datetime

from customer.models.customer import Customer
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from rest_framework.status import HTTP_400_BAD_REQUEST
from sites.models.site import Site

from common.const import DATE_FORMAT_EN
from common.error_code import StatusCode
from common.framework.exception import APIException, InvalidException
from common.utils.excel_utils import Workbook

logger = logging.getLogger(__name__)


class ExcelService(object):
    @classmethod
    def file_import(cls, excel_file=None, excel_file_name=None, sheet_name=None):
        """
        import data set record from excel
        :param excel_file: excel file object or excel file contents
        :param excel_file_name: excel file name
        :param sheet_name: excel sheet name
        :return: None
        """
        workbook = Workbook.open(excel_file_name=excel_file_name, excel_file=excel_file)
        workbook_data = list(cls.read_workbook_data(workbook, sheet_name))
        try:
            assembled_data = [cls.assemble_excel_data(data) for data in workbook_data]
        except Exception:
            raise ExcelException("excel格式错误！")
        cls.save_workbook_data(assembled_data)

    @classmethod
    def save_workbook_data(cls, workbook_data: list):
        if not workbook_data:
            raise InvalidException(
                "this file is empty", code=StatusCode.IMPORT_EXCEL_IS_EMPTY.value,
            )
        for data_list in workbook_data:
            try:
                customer_id = cls.crete_or_update_customer(data_list[0])
                site_id = cls.crete_or_update_site(data_list[1], customer_id)
                equipment_id = cls.crete_or_update_equipment(data_list[2], site_id)
                cls.crete_or_update_point(data_list[3], equipment_id)
            except Exception as e:
                logger.exception(f"save workbook data error, exception: {e=}")

    @classmethod
    def read_workbook_data(cls, workbook, sheet_name=None):
        for column in workbook.get_columns(
            sheet_name=sheet_name, r_offset=3, c_offset=2
        ):
            result = []
            for value in column:
                if isinstance(value, datetime):
                    value = value.strftime(DATE_FORMAT_EN)
                result.append(value)
            if any(value.strip() != "" for value in result):
                yield result

    @classmethod
    def assemble_excel_data(cls, data: list):
        customer = {
            "name": data[0],
            "administrative_division": {
                "province": data[1],
                "city": data[2],
                "region": data[3],
            },
            "remarks": data[4],
        }
        o_site_location = data[10].replace(" ", "").split(",")
        if len(o_site_location) == 1:
            o_site_location = data[10].replace(" ", "").split("，")
        site = {
            "name": data[5],
            "voltage_level": data[6],
            "administrative_division": {
                "province": data[7],
                "city": data[8],
                "region": data[9],
            },
            "site_location": o_site_location,
            "remarks": data[11],
        }
        equipment = {
            "device_name": data[12],
            "device_type": data[13],
            "voltage_level": data[14],
            "operation_number": data[15],
            "asset_number": data[16],
            "device_model": data[17],
            "factory_number": data[18],
            "remarks": data[19],
        }
        point = {
            "measure_name": data[20],
            "sensor_number": data[21],
            "measure_type": data[22],
            "remarks": data[23],
        }
        return [customer, site, equipment, point]

    @classmethod
    def crete_or_update_customer(cls, customer_dict: dict) -> str:
        customer = Customer.objects(name=customer_dict["name"]).first()
        if customer:
            customer.update(**customer_dict)
        else:
            customer = Customer(**customer_dict)
            customer.save()
        return str(customer.pk)

    @classmethod
    def crete_or_update_site(cls, site_dict: dict, customer_id: str) -> str:
        site = Site.objects(customer=customer_id, name=site_dict["name"]).first()
        site_dict.update({"customer": customer_id})
        if site:
            site.update(**site_dict)
        else:
            site = Site(**site_dict)
            site.save()
        return str(site.pk)

    @classmethod
    def crete_or_update_equipment(cls, equipment_dict: dict, site_id: str) -> str:
        equipment = ElectricalEquipment.objects(
            site_id=site_id, device_name=equipment_dict["device_name"]
        ).first()
        equipment_dict.update({"site_id": site_id})
        if equipment:
            equipment.update(**equipment_dict)
        else:
            equipment = ElectricalEquipment(**equipment_dict)
            equipment.save()
        return str(equipment.pk)

    @classmethod
    def crete_or_update_point(cls, point_dict: dict, equipment_id: str) -> str:
        point = MeasurePoint.objects(
            equipment_id=equipment_id, measure_name=point_dict["measure_name"]
        ).first()
        point_dict.update({"equipment_id": equipment_id})
        if point:
            point.update(**point_dict)
        else:
            point = MeasurePoint(**point_dict)
            point.save()
        return str(point.pk)


class ExcelException(APIException):
    status_code = HTTP_400_BAD_REQUEST
