import logging

from rest_framework.status import HTTP_201_CREATED
from sites.services.site_service import SiteService
from sites.validators.sites_serializers import (
    BaseSiteSerializer,
    CreateSiteSerializer,
    GetCustomerSitesSerializer,
    UpdateSiteSerializer,
    DeleteSiteSerializer,
)

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomerSitesView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("POST",),
        ),
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
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("DELETE", "PUT"),
        ),
    )

    def get(self, request, customer_id, site_id):
        _, context = self.get_validated_data(
            BaseSiteSerializer, customer_id=customer_id, site_id=site_id
        )
        site = context["site"]
        return BaseResponse(data=site.to_dict)

    def put(self, request, customer_id, site_id):
        user = request.user
        data, context = self.get_validated_data(UpdateSiteSerializer, site_id=site_id)
        logger.info(f"{user.username} request update {site_id=} with {data=}")
        name = data.get("name")
        administrative_division = data.get("administrative_division")
        remarks = data.get("remarks")
        voltage_level = data.get("voltage_level")
        site_location = data.get("site_location")
        site = context["site"]
        update_fields = {}
        if name:
            update_fields["name"] = name
        if administrative_division:
            update_fields["administrative_division"] = administrative_division
        if remarks:
            update_fields["remarks"] = remarks
        if voltage_level:
            update_fields["voltage_level"] = voltage_level
        if site_location:
            update_fields["site_location"] = site_location
        if update_fields:
            site.update(**update_fields)
        return BaseResponse(data=update_fields)

    def delete(self, request, customer_id, site_id):
        # todo delete site resource include what?
        user = request.user
        data, context = self.get_validated_data(
            DeleteSiteSerializer, site_id=site_id
        )
        logger.info(f"{user.username} request delete {site_id=} in {customer_id=} with {data}")
        site = context["site"]
        clear_resource = data["clear_resource"]
        SiteService.delete_site(site, clear_resource)
        return BaseResponse()
