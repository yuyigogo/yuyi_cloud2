import logging

from common.framework.response import BaseResponse
from common.framework.view import BaseView
from customer.models.customer import Customer
from navigation.services.equipment_navigation_service import SiteNavigationService

logger = logging.getLogger(__name__)


class GatewayTreesView(BaseView):
    def get(self, request):
        """
        网关配置树形图
        :param request:
        :return:
        """
        user = request.user
        customer_id = user.customer
        logger.info(f"{user.username} request GatewayTrees with for {customer_id=}")
        if user.is_cloud_or_client_super_admin():
            # get all customer tree infos
            data = SiteNavigationService.get_customers_tree_infos(
                customer_id, is_gateway_tree=True
            )
        else:
            # get corresponding customer's tree info
            customer = Customer.objects.only("name").get(pk=customer_id)
            query_sites = user.sites if user.is_normal_admin() else None
            data = list(
                SiteNavigationService.get_one_customer_tree_infos(
                    customer, is_gateway_tree=True, site_ids=query_sites
                )
            )
        return BaseResponse(data=data)
