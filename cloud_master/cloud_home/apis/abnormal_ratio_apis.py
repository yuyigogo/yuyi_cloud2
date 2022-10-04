from cloud_home.services.abnormal_ratio_service import AbnormalRatioService

from common.framework.response import BaseResponse
from common.framework.view import BaseView


class CustomerAbnormalRatioView(BaseView):
    def get(self, request, customer_id):
        data = AbnormalRatioService.get_customer_or_site_abnormal_ratio(
            customer_id=customer_id
        )
        return BaseResponse(data=data)


class SiteAbnormalRatioView(BaseView):
    def get(self, request, site_id):
        data = AbnormalRatioService.get_customer_or_site_abnormal_ratio(site_id=site_id)
        return BaseResponse(data=data)
