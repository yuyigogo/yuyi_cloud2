import logging

from rest_framework.status import HTTP_201_CREATED
from sites.services.site_service import SiteService
from sites.validators.sites_serializers import (
    CreateSiteSerializer,
    GetCustomerSitesSerializer,
)

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomerSitesView(BaseView):
    permission_classes = (
        PermissionFactory(RoleLevel.CLOUD_SUPER_ADMIN, method_list=("POST",)),
        PermissionFactory(RoleLevel.CLIENT_SUPER_ADMIN, method_list=("POST",)),
    )

    def get(self, request, customer_id):
        user = request.user
        self.get_validated_data(GetCustomerSitesSerializer, customer_id=customer_id)
        sites = SiteService(user, customer_id).get_sites_by_customer_id()
        data = [site.to_dict() for site in sites]
        return BaseResponse(data=data)

    def post(self, request, customer_id):
        user = request.user
        data, _ = self.get_validated_data(CreateSiteSerializer, customer_id=customer_id)
        logging.info(
            f"{user.username} request create site for {customer_id=} with {data=}"
        )
        service = SiteService(user, customer_id)
        site = service.create_site(
            name=data["name"],
            administrative_division=data["administrative_division"],
            voltage_level=data["voltage_level"],
            site_location=data.get("site_location", ""),
            remarks=data.get("remarks", ""),
        )
        return BaseResponse(data=site.to_dict(), status_code=HTTP_201_CREATED)


class CustomerSiteView(BaseView):
    def get(self, request, customer_id, site_id):
        pass

    def put(self, request, customer_id, site_id):
        pass

    def delete(self, request, customer_id, site_id):
        pass
