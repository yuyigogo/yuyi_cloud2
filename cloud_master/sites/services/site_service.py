from typing import Optional, Union

from bson import ObjectId
from sites.models.site import Site
from user_management.models.user import CloudUser

from common.framework.service import BaseService


class SiteService(BaseService):
    def __init__(self, user: CloudUser, customer_id: Union[ObjectId, str]):
        self.user = user
        self.customer_id = customer_id

    def get_sites_by_customer_id(self) -> list:
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
    def delete_site(cls, site: Site, customer_id: Union[ObjectId, str] = None):
        # remove the deleted site_id from user.sites
        # if this is ALL customer, should query without customer
        site_id = site.pk
        users = CloudUser.objects.filter(sites__in=[site_id])
        if customer_id:
            users = users.filter(customer=customer_id)
        for user in users:
            user.sites.remove(site_id)
            user.update(sites=user.sites)
        site.delete()
