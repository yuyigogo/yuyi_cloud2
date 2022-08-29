from typing import List, Optional, Union

from bson import ObjectId
from equipment_management.models.gateway import GateWay
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from mongoengine import queryset
from sites.models.site import Site
from user_management.models.user import CloudUser

from common.const import ALL
from common.framework.service import BaseService


class SiteService(BaseService):
    def __init__(self, user: CloudUser, customer_id: Union[ObjectId, str]):
        self.user = user
        self.customer_id = customer_id

    def get_sites_by_customer_id(self) -> queryset:
        return Site.objects.filter(customer=self.customer_id)

    def create_site(
        self,
        name: str,
        administrative_division: str,
        voltage_level: int,
        site_location: List[float],
        remarks: Optional[str] = None,
    ) -> Site:
        site = Site(
            name=name,
            customer=self.customer_id,
            administrative_division=administrative_division,
            voltage_level=voltage_level,
            site_location=site_location,
            remarks=remarks,
        )
        site.save()
        return site

    @classmethod
    def delete_site(cls, site: Site, clear_resource: bool):
        site_id = site.pk
        gateways = GateWay.objects.filter(site_id=site_id)
        client_numbers = gateways.values_list("client_number")
        equipments = ElectricalEquipment.objects.filter(site_id=site_id)
        equipment_ids = equipments.values_list("id")
        points = MeasurePoint.objects.filter(equipment_id__in=equipment_ids)
        cls.delete_points(points, clear_resource=clear_resource)
        gateways.delete()
        equipments.delete()
        site.delete()
        users = CloudUser.objects.filter(sites__in=[site_id])
        delete_users, remove_site_users = [], []
        for user in users:
            if len(user.sites) > 1:
                remove_site_users.append(user.pk)
            else:
                delete_users.append(user.pk)
        CloudUser.object(id__in=delete_users).delete()
        CloudUser.objects(id__in=remove_site_users).update(
            __raw__={"$pull": {"sites": {site_id}}}
        )
        # clear client_id from redis
        for client_id in client_numbers:
            cls.remove_client_id_from_redis(client_id)

    @classmethod
    def named_all_site_id(cls):
        return str(Site.objects.get(name=ALL).pk)

    @classmethod
    def get_user_sites_info(cls, site_ids: list) -> list:
        sites = Site.objects.filter(id__in=site_ids)
        return [
            {
                "id": str(site.id),
                "name": site.name,
                "customer": str(site.customer),
                "administrative_division": site.administrative_division,
                "remarks": site.remarks,
                "voltage_level": site.voltage_level,
                "site_location": site.site_location,
            }
            for site in sites
        ]
