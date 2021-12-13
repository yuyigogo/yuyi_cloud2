from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from customer.models.customer import Customer
from equipment_management.models.gateway import GateWay
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from sites.models.site import Site

from common.framework.service import BaseService


class SiteNavigationService(BaseService):
    @classmethod
    def get_latest_sensor_info(cls, sensor_number: str, sensor_type: str) -> dict:
        mongo_col = MONGO_CLIENT[sensor_type]
        sensor_data = mongo_col.find_one({"sensor_id": sensor_number, "is_new": True},)
        return bson_to_dict(sensor_data) if sensor_data else {}

    @classmethod
    def get_all_sensors_in_equipment(cls, equipment: ElectricalEquipment) -> list:
        equipment_sensors = []
        points = MeasurePoint.objects.only(
            "measure_name", "measure_type", "sensor_number"
        ).filter(equipment_id=equipment.pk)
        for point in points:
            sensor_number = point.sensor_number
            sensor_type = point.measure_type
            equipment_sensors.append(
                {
                    "device_name": equipment.device_name,
                    "point_name": point.measure_name,
                    "point_id": str(point.pk),
                    "type": sensor_type,
                    "sensor_id": point.sensor_number,
                    "sensor_info": cls.get_latest_sensor_info(
                        sensor_number, sensor_type
                    ),
                }
            )
        return equipment_sensors

    @classmethod
    def get_all_sensors_in_site(cls, site: Site) -> list:
        site_sensors = []
        equipments = ElectricalEquipment.objects.only(
            "device_name", "device_type"
        ).filter(site_id=site.pk)
        for equipment in equipments:
            site_sensors.extend(cls.get_all_sensors_in_equipment(equipment))
        return site_sensors

    @classmethod
    def get_all_sensors_in_customer(cls, customer: Customer) -> list:
        customer_sensors = []
        sites = Site.objects.only("id").filter(customer=customer.pk)
        for site in sites:
            customer_sensors.extend(cls.get_all_sensors_in_site(site))
        return customer_sensors

    @classmethod
    def get_one_customer_tree_infos(
        cls, customer: Customer, add_point: bool = False, is_gateway_tree: bool = False
    ) -> dict:
        customer_tree_info = {
            "id": str(customer.pk),
            "label": customer.name,
            "type": "customer",
            "children": [],
        }
        sites = Site.objects.only("customer", "name").filter(customer=customer.pk)
        customer_tree_info["children"] = [
            cls.get_one_site_tree_infos(site, add_point, is_gateway_tree)
            for site in sites
        ]
        return customer_tree_info

    @classmethod
    def get_one_site_tree_infos(
        cls, site: Site, add_point: bool = False, is_gateway_tree: bool = False
    ) -> dict:
        site_tree_info = {
            "parend_id": str(site.customer),
            "label": site.name,
            "id": str(site.pk),
            "type": "site",
            "children": [],
        }
        if not is_gateway_tree:
            equipments = ElectricalEquipment.objects.only(
                "device_name", "site_id"
            ).filter(site_id=site.pk)
            site_tree_info["children"] = [
                cls.get_one_equipment_tree_infos(equipment, add_point)
                for equipment in equipments
            ]
        else:
            gateways = GateWay.objects.only(
                "name", "client_number", "sensor_ids", "site_id"
            ).filter(site_id=site.pk)
            site_tree_info["children"] = [
                cls.get_one_gateway_tree_infos(gateway) for gateway in gateways
            ]
        return site_tree_info

    @classmethod
    def get_one_equipment_tree_infos(
        cls, equipment: ElectricalEquipment, add_point: bool = False
    ) -> dict:
        equipment_tree_info = {
            "parend_id": str(equipment.site_id),
            "label": equipment.device_name,
            "id": str(equipment.pk),
            "type": "equipment",
            "children": [],
        }
        if add_point:
            points = MeasurePoint.objects.only("measure_name", "equipment_id").filter(
                equipment_id=equipment.pk
            )
            equipment_tree_info["children"] = [
                {
                    "label": point.measure_name,
                    "id": str(point.pk),
                    "type": "point",
                    "parend_id": str(point.equipment_id),
                }
                for point in points
            ]
        return equipment_tree_info

    @classmethod
    def get_one_gateway_tree_infos(cls, gateway: GateWay) -> dict:
        gateway_tree_info = {
            "parend_id": str(gateway.site_id),
            "label": gateway.name,
            "id": str(gateway.pk),
            "type": "gateway",
            "children": [],
        }
        # todo add sensor infos to children
        return gateway_tree_info

    @classmethod
    def get_customers_tree_infos(
        cls,
        named_all_customer: str,
        add_point: bool = False,
        is_gateway_tree: bool = False,
    ) -> list:
        customers = Customer.objects.filter(id__ne=named_all_customer)
        return [
            cls.get_one_customer_tree_infos(customer, add_point, is_gateway_tree)
            for customer in customers
        ]
