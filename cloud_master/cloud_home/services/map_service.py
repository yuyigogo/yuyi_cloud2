from collections import defaultdict
from typing import Optional

from customer.models.customer import Customer
from equipment_management.models.sensor_config import SensorConfig
from sites.models.site import Site

from common.const import ALL, SITE_UNPROCESSED_NUM
from common.framework.service import BaseService
from common.storage.redis import normal_redis


class MapService(BaseService):
    @classmethod
    def get_sensor_num_in_site(cls, site_ids: list) -> dict:
        configs = SensorConfig.objects.only("site_id").filter(site_id__in=site_ids)
        sensor_num_infos = defaultdict(int)
        for config in configs:
            sensor_num_infos[config.site_id] += 1
        return sensor_num_infos

    @classmethod
    def get_map_tress_info(cls, customer_id: Optional[str] = None) -> list:
        map_trees_info = []
        if customer_id:
            info_dict = {}
            customer = Customer.objects.only("name").get(id=customer_id)
            info_dict["type"] = "customer"
            info_dict["label"] = customer.name
            info_dict["id"] = customer_id
            sites = Site.objects.only("name", "site_location").filter(
                customer=customer_id
            )
            sensor_num_infos = cls.get_sensor_num_in_site(sites.values_list("id"))
            info_dict["children"] = [
                {
                    "type": "site",
                    "label": site.name,
                    "id": str(site.pk),
                    "sensor_num": sensor_num_infos.get(site.pk, 0),
                    "unprocessed_num": normal_redis.get(
                        f"{SITE_UNPROCESSED_NUM}{str(site.pk)}"
                    ),
                }
                for site in sites
            ]
            map_trees_info.append(info_dict)
        else:
            customers = Customer.objects.only("name").filter(name__ne=ALL)
            customer_infos = {
                customer.pk: {
                    "type": "customer",
                    "label": customer.name,
                    "id": str(customer.pk),
                }
                for customer in customers
            }
            sites = Site.objects.only("name", "site_location", "customer").filter(
                customer__in=customer_infos.keys()
            )
            sensor_num_infos = cls.get_sensor_num_in_site(sites.values_list("id"))
            site_info = defaultdict(list)
            for site in sites:
                site_id = site.pk
                # sit_unprocessed_key = f"{SITE_UNPROCESSED_NUM}{str(site_id)}"
                # unprocessed_num = normal_redis.get(sit_unprocessed_key)
                # if not unprocessed_num:
                #     unprocessed_num = 0
                site_info[site.customer].append(
                    {
                        "type": "site",
                        "label": site.name,
                        "id": str(site_id),
                        "sensor_num": sensor_num_infos.get(site_id, 0),
                        "unprocessed_num": normal_redis.get(
                            f"{SITE_UNPROCESSED_NUM}{str(site_id)}"
                        ),
                    }
                )
            for customer_id, customer_info_dict in customer_infos.items():
                children = site_info.get(customer_id, [])
                customer_info_dict["children"] = children
                map_trees_info.append(customer_info_dict)
        return map_trees_info
