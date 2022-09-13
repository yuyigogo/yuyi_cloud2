import logging

from cloud_home.services.map_service import MapService

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class MapTressView(BaseView):
    def get(self, request):
        user = request.user
        logger.info(f"{user.username} request map tress")
        if user.is_cloud_or_client_super_admin():
            customer_id = None
        else:
            customer_id = str(user.customer)
        map_trees = MapService.get_map_tress_info(customer_id)
        return BaseResponse(data=map_trees)
