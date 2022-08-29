import logging

from customer.models.customer import Customer
from navigation.services.equipment_navigation_service import SiteNavigationService

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomerTreesView(BaseView):
    def get(self, request):
        """
        公司树形图
        :param request:
        :return:
        """
        user = request.user
        customer_id = user.customer
        add_point = bool(request.GET.get("add_point", 0))
        logger.info(
            f"{user.username} request CustomerTrees with {add_point=} for {customer_id=}"
        )
        if user.is_cloud_or_client_super_admin():
            # get all customer tree infos
            data = SiteNavigationService.get_customers_tree_infos(
                customer_id, add_point
            )
        else:
            # get corresponding customer's tree info
            customer = Customer.objects.only("name").get(pk=customer_id)
            query_sites = user.sites if user.is_normal_admin() else None
            data = [
                SiteNavigationService.get_one_customer_tree_infos(
                    customer, add_point, site_ids=query_sites
                )
            ]
        return BaseResponse(data=data)
