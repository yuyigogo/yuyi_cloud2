import logging

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class GatewayTreesView(BaseView):
    def get(self, request):
        user = request.user
        customer_id = user.customer
        logger.info(
            f"{user.username} request GatewayTrees with for {customer_id=}"
        )
        # if user.is_cloud_or_client_super_admin():
        #     # get all customer tree infos
        #     data = SiteNavigationService.get_customers_tree_infos(
        #         customer_id, add_point
        #     )
        # else:
        #     # get corresponding customer's tree info
        #     customer = Customer.objects.only("name").get(pk=customer_id)
        #     data = list(
        #         SiteNavigationService.get_one_customer_tree_infos(customer, add_point)
        #     )
        # return BaseResponse(data=data)
