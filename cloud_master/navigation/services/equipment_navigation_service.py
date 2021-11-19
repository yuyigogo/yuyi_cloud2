from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from customer.models.customer import Customer
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
    def get_all_sensors_in_equipment(cls, equipment: ElectricalEquipment) -> dict:
        equipment_sensors = {
            "id": str(equipment.pk),
            "name": equipment.device_name,
            "type": equipment.device_type,
            "sensor_infos": [],
        }
        points = MeasurePoint.objects.only(
            "measure_name", "measure_type", "sensor_number"
        ).filter(equipment_id=equipment.pk)
        for point in points:
            sensor_number = point.sensor_number
            sensor_type = point.measure_type
            equipment_sensors["sensor_infos"].append(
                {
                    "name": point.measure_name,
                    "id": str(point.pk),
                    "type": sensor_type,
                    "sensor_infos": cls.get_latest_sensor_info(
                        sensor_number, sensor_type
                    ),
                }
            )
        return equipment_sensors

    @classmethod
    def get_all_sensors_in_site(cls, site: Site) -> dict:
        site_sensors = {
            "id": str(site.pk),
            "name": site.name,
            "sensor_infos": [],
        }
        equipments = ElectricalEquipment.objects.only(
            "device_name", "device_type"
        ).filter(site_id=site.pk)
        site_sensors["sensor_infos"] = [
            cls.get_all_sensors_in_equipment(equipment) for equipment in equipments
        ]
        return site_sensors

    @classmethod
    def get_all_sensors_in_customer(cls, customer: Customer) -> dict:
        customer_sensors = {
            "id": str(customer.pk),
            "name": customer.name,
            "sensor_infos": [],
        }
        sites = Site.objects.only("name").filter(customer=customer.pk)
        customer_sensors["sensor_infos"] = [
            cls.get_all_sensors_in_site(site) for site in sites
        ]
        return customer_sensors
