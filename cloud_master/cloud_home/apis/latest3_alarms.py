import logging

from cloud_home.services.latest3_alarms_service import LatestAlarmsService
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class LatestAlarmsView(BaseView):
    def get(self, request):
        user = request.user
        logger.info(f"{user.username} request latest 3 alarm infos")
        service = LatestAlarmsService(user)
        data = service.get_latest3_alarms()
        return BaseResponse(data=data)
