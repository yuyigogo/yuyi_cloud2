from datetime import datetime

from customer.models.customer import Customer
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from sites.models.site import Site

from common.const import DATE_FORMAT_EN
from common.error_code import StatusCode
from common.framework.exception import InvalidException
from common.utils.excel_utils import Workbook


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
        assembled_data = [cls.assemble_excel_data(data) for data in workbook_data]
        cls.save_workbook_data(assembled_data)

    @classmethod
    def save_workbook_data(cls, workbook_data: list):
        if not workbook_data:
            raise InvalidException(
                "this file is empty", code=StatusCode.IMPORT_EXCEL_IS_EMPTY.value,
            )
        for data_list in workbook_data:
            customer_id = cls.crete_or_update_customer(data_list[0])
            site_id = cls.crete_or_update_site(data_list[1], customer_id)
            equipment_id = cls.crete_or_update_equipment(data_list[2], site_id)
            cls.crete_or_update_point(data_list[3], equipment_id)

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
            "administrative_division": f"{data[1]}-{data[2]}-{data[3]}",
            "remarks": data[4],
        }
        site = {
            "name": data[5],
            "voltage_level": data[6],
            "administrative_division": data[7],
            "site_location": data[8].replace(" ", "").split(","),
            "remarks": data[9],
        }
        equipment = {
            "device_name": data[10],
            "device_type": data[11],
            "voltage_level": data[12],
            "operation_number": data[13],
            "asset_number": data[14],
            "device_model": data[15],
            "factory_number": data[16],
            "remarks": data[17],
        }
        point = {
            "measure_name": data[18],
            "sensor_number": data[19],
            "measure_type": data[20],
            "remarks": data[21],
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