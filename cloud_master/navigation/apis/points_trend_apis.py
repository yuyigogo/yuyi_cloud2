import logging

from navigation.services.points_trend_service import PointsTrendService
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class PointsTrendView(BaseView):
    def post(self, request):
        """
        get points trend data
        :param : {
                    "point_ids": ["61939faab767c4804ca0a25f", "6193a4bfb767c4804ca0a260"],
                    "start_date": "2021-11-13",
                    "end_date": "2021-11-29"
        }
        :return:
        """
        point_list = request.data.get("point_ids", [])
        start_date = request.data.get("start_date", "")
        end_date = request.data.get("end_date", "")
        # todo check param
        sensor_trend_data = PointsTrendService.get_points_trend_data(
            point_list, start_date, end_date
        )
        return BaseResponse(data=sensor_trend_data)
