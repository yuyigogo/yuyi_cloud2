from typing import Optional

from customer.models.customer import Customer
from equipment_management.models.gateway import GateWay
from mongoengine import Q
from sites.models.site import Site
from user_management.models.user import CloudUser

from common.const import ALL
from common.framework.service import BaseService
from common.utils.excel_utils import data_to_xlsx


class GatewayExportService(BaseService):
    def __init__(self, user: CloudUser, customer_id: str, site_id: Optional[str]):
        self.user = user
        self.customer_id = customer_id
        self.site_id = site_id

    def is_export_all(self):
        return self.customer_id == ALL

    def get_gateways(self):
        if self.is_export_all():
            gateways = GateWay.objects.filter().as_pymongo()
        else:
            if self.site_id is None or self.site_id == ALL:
                gateway_query = Q(customer=self.customer_id)
            else:
                gateway_query = Q(customer=self.customer_id, site_id=self.site_id)
            gateways = GateWay.objects.filter(gateway_query).as_pymongo()
        customer_ids, site_ids = set(), set()
        for gateway_dict in gateways:
            customer_ids.add(gateway_dict.get("customer"))
            site_ids.add(gateway_dict.get("site_id"))
        customer_id_name, site_id_name = self.get_customer_site_infos(
            customer_ids, site_ids
        )
        return customer_id_name, site_id_name, gateways

    @classmethod
    def get_customer_site_infos(cls, customer_ids: set, site_ids: set) -> tuple:
        customer_id_name = dict(
            Customer.objects.filter(id__in=customer_ids).values_list("id", "name")
        )
        site_id_name = dict(
            Site.objects.filter(id__in=site_ids).values_list("id", "name")
        )
        return customer_id_name, site_id_name

    @classmethod
    def get_excel_header(cls) -> list:
        # first_header_data = ["序号", "公司", "站点", "监测主机", "", ""]
        second_header_data = ["公司名称", "站点名称", "主机名称", "主机编号", "备注"]
        return [second_header_data]

    def get_excel_body(self) -> list:
        excel_body = []
        customer_id_name, site_id_name, gateways = self.get_gateways()
        for gateway_dict in gateways:
            excel_values = []
            customer_id = gateway_dict.get("customer")
            site_id = gateway_dict.get("site_id")
            customer_name = customer_id_name.get(customer_id, "")
            site_name = site_id_name.get(site_id)
            gateway_name = gateway_dict.get("name")
            client_number = gateway_dict.get("client_number")
            remarks = gateway_dict.get("remarks", "")
            excel_values.extend(
                [customer_name, site_name, gateway_name, client_number, remarks]
            )
            excel_body.append(excel_values)
        return excel_body

    def get_excel_data(self) -> list:
        excel_data = self.get_excel_header()
        excel_data += self.get_excel_body()
        return excel_data

    def get_excel_content(self) -> bytes:
        excel_data = self.get_excel_data()
        return data_to_xlsx(excel_data, color_lines=[1])
