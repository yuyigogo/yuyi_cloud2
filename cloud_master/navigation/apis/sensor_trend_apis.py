import logging

from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from navigation.services.sensor_trend_service import SensorTrendService
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class SensorTrendView(BaseView):
    def post(self, request):
        """
        get sensor trend data
        :param : {
                    "sensor_list": [
                        {
                            "sensor_id": "20210b0100010003",
                            "sensor_type": "ae"
                        },
                        {
                            "sensor_id": "20210b0100010003",
                            "sensor_type": "tev"
                        }
                    ],
                    "start_date": "2021-11-15",
                    "end_date": "2021-11-16"
                }
        :return:
        """
        sensor_list = request.POST.get('sensor_list', [
            {
                "sensor_id": "20210b0100010003",
                "sensor_type": "ae"
            },
            {
                "sensor_id": "58475012002e0062",
                "sensor_type": "ae"
            }
        ])
        start_date = request.POST.get('start_date', "2021-11-15")
        end_date = request.POST.get('end_date', "2021-11-16")
        # todo check param
        try:
            sensor_trend_data = SensorTrendService.get_sensor_trend_data(sensor_list, start_date, end_date)
        except Exception as e:
            logger.info(f"{e}")
            return BaseResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return BaseResponse(data=sensor_trend_data)
