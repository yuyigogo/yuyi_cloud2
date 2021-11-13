from typing import Optional, Union

from bson import ObjectId
from mongoengine import queryset

from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from sites.models.site import Site
from user_management.models.user import CloudUser

from common.const import ALL
from common.framework.service import BaseService


class SiteService(BaseService):
    def __init__(self, user: CloudUser, customer_id: Union[ObjectId, str]):
        self.user = user
        self.customer_id = customer_id

    def get_sites_by_customer_id(self) -> queryset:
        sites = Site.objects.filter()
        if self.user.is_cloud_or_client_super_admin():
            return sites
        else:
            return sites.filter(customer=self.customer_id)

    def create_site(
        self,
        name: str,
        administrative_division: str,
        voltage_level: int,
        site_location: Optional[list] = None,
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
        if clear_resource:
            equipments = ElectricalEquipment.objects.filter(site_id=site_id)
            equipment_ids = equipments.values_list("id")
            MeasurePoint.objects.filter(equipment_id__in=equipment_ids).delete()
            equipments.delete()
        CloudUser.objects.filter(sites__in=[site_id]).delete()
        site.delete()

    @classmethod
    def named_all_site(cls):
        return Site.objects.get(name=ALL)

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
