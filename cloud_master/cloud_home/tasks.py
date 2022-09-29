from typing import Optional

from bson import ObjectId
from cloud_home.models.status_statistics import CStatusStatistic, SStatusStatistic
from cloud_home.services.status_statistics_service import StatusStatisticService
from customer.models.customer import Customer
from pymongo import UpdateOne
from sites.models.site import Site

from common.const import ALL
from common.scheduler import cloud_task


@cloud_task
def async_customer_status_statistic(customer_ids: Optional[list] = None):
    """
    1. counting customer/site status infos;
    2. the status infos include:
        a. asset info;
        b. equipment status info;
        c. sensor online ratio info;
        d. point distribution info;
    3. insert those info into c_status_statistic/s_status_statistic
    """
    if customer_ids is None:
        # get all customer_ids
        customer_ids = Customer.objects().values_list("id")
        customer_ids = list(map(str, customer_ids))
    bulk_operations = []
    for customer_id in customer_ids:
        service = StatusStatisticService(customer_id=customer_id)
        asset_info = service.get_customer_asset_info()
        equipment_status_info = service.get_customer_equipment_status_statistics()
        sensor_online_ratio = service.get_customer_or_site_sensor_online_ratio()
        point_distribution_info = service.get_customer_or_site_point_distribution_info()
        bulk_operations.append(
            UpdateOne(
                {"customer_id": ObjectId(customer_id)},
                {
                    "$set": {
                        "asset_info": asset_info,
                        "equipment_status_info": equipment_status_info,
                        "sensor_online_ratio": sensor_online_ratio,
                        "point_distribution_info": point_distribution_info,
                    }
                },
                upsert=True,
            )
        )
    collection = CStatusStatistic._get_collection()
    collection.bulk_write(bulk_operations, ordered=False)


@cloud_task
def async_site_status_statistic(site_ids: Optional[list] = None):
    update_named_all_site = False
    if site_ids is None:
        # get all site_ids
        update_named_all_site = True
        site_ids = Site.objects(name__ne=ALL).values_list("id")
        site_ids = list(map(str, site_ids))
    bulk_operations = []
    for site_id in site_ids:
        service = StatusStatisticService(site_id=site_id)
        asset_info = service.get_site_asset_info()
        equipment_status_info = service.get_site_equipment_status_statistics_in_site()
        sensor_online_ratio = service.get_customer_or_site_sensor_online_ratio()
        point_distribution_info = service.get_customer_or_site_point_distribution_info()
        bulk_operations.append(
            UpdateOne(
                {"site_id": ObjectId(site_id)},
                {
                    "$set": {
                        "asset_info": asset_info,
                        "equipment_status_info": equipment_status_info,
                        "sensor_online_ratio": sensor_online_ratio,
                        "point_distribution_info": point_distribution_info,
                    }
                },
                upsert=True,
            )
        )
    if update_named_all_site:
        site = Site.objects.only("customer").get(name=ALL)
        c_all_info = CStatusStatistic.objects.get(customer_id=site.customer)
        bulk_operations.append(
            UpdateOne(
                {"site_id": site.id},
                {
                    "$set": {
                        "asset_info": c_all_info.asset_info,
                        "equipment_status_info": c_all_info.equipment_status_info,
                        "sensor_online_ratio": c_all_info.sensor_online_ratio,
                        "point_distribution_info": c_all_info.point_distribution_info,
                    }
                },
                upsert=True,
            )
        )
    collection = SStatusStatistic._get_collection()
    collection.bulk_write(bulk_operations, ordered=False)
