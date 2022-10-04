from datetime import datetime
from typing import Optional

from cloud_home.models.status_statistics import CAbnormalRatio, SAbnormalRatio
from dateutil.relativedelta import relativedelta
from mongoengine import Q

from common.framework.service import BaseService


class AbnormalRatioService(BaseService):
    @classmethod
    def get_customer_or_site_abnormal_ratio(
        cls, customer_id: Optional[str] = None, site_id: Optional[str] = None
    ):
        assert customer_id or site_id, "AbnormalRatioService's error"
        end_date = datetime.now()
        start_date = end_date - relativedelta(years=1)
        query_match = Q(create_date__lte=start_date, create_date__gte=end_date)
        if customer_id:
            query_match &= Q(customer_id=customer_id)
            abnormal_ratios = CAbnormalRatio.objects.filter(query_match).order_by(
                "create_date"
            )
        else:
            query_match &= Q(site_id=site_id)
            abnormal_ratios = SAbnormalRatio.objects.filter(query_match).order_by(
                "create_date"
            )
        return dict(abnormal_ratios.values_list("create_date", "ratio"))
