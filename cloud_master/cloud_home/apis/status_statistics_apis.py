from cloud_home.validators.status_statistics_serializers import (
    CustomerAssetSerializer,
    SiteAssetSerializer,
)

from common.const import ALL
from common.framework.response import BaseResponse
from common.framework.view import BaseView


class CustomerStatusView(BaseView):
    def get(self, request, customer_id):
        """get customer assets"""
        data, _ = self.get_validated_data(
            CustomerAssetSerializer, customer_id=customer_id
        )
        customer = data["customer"]
        if customer.name == ALL:
            # get all assets
            assent_infos = AssetCountService.get_customer_assets()
        else:
            # get asset in the customer
            assent_infos = AssetCountService.get_customer_assets()
        return BaseResponse(data=assent_infos)


class SiteStatusView(BaseView):
    def get(self, request, site_id):
        self.get_validated_data(SiteAssetSerializer)
        return BaseResponse(data=assent_infos)
