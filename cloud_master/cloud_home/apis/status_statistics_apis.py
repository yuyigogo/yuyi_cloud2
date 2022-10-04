from cloud_home.services.status_statistics_service import StatusStatisticApiService
from cloud_home.validators.status_statistics_serializers import (
    CustomerStatusSerializer,
    SiteStatusSerializer,
)

from common.framework.response import BaseResponse
from common.framework.view import BaseView


class CustomerStatusView(BaseView):
    def get(self, request, customer_id):
        """get customer status infos"""
        data, _ = self.get_validated_data(
            CustomerStatusSerializer, customer_id=customer_id
        )
        service = StatusStatisticApiService(data["is_refresh"], customer_id=customer_id)
        status_info = service.get_customer_or_site_status_infos()
        return BaseResponse(data=status_info)


class SiteStatusView(BaseView):
    def get(self, request, site_id):
        data, _ = self.get_validated_data(SiteStatusSerializer)
        service = StatusStatisticApiService(data["is_refresh"], site_id=site_id)
        status_info = service.get_customer_or_site_status_infos()
        return BaseResponse(data=status_info)
