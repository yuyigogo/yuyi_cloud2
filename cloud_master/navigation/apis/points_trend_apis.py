import logging

from navigation.services.points_trend_service import PointsTrendService
from common.framework.response import BaseResponse
from common.framework.view import BaseView
from navigation.validators.point_trend_sereializers import PointTrendSerializer

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
        data, _ = self.get_validated_data(PointTrendSerializer)
        point_ids = data["point_ids"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        logger.info(f"{request.user.username} request points trend with {data=}")
        sensor_trend_data = PointsTrendService.get_points_trend_data(
            point_ids, start_date, end_date
        )
        return BaseResponse(data=sensor_trend_data)
