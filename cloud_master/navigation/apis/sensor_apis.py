import logging

from bson import ObjectId

from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from rest_framework.status import HTTP_404_NOT_FOUND

from common.const import SensorType
from common.framework.exception import APIException
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class SensorDetailsView(BaseView):
    def get(self, request, pk):
        sensor_type = request.query_params.get("sensor_type")
        if sensor_type not in SensorType.values():
            raise APIException(f"invalid {sensor_type=}!")
        try:
            mongo_col = MONGO_CLIENT[sensor_type]
            data = mongo_col.find_one({"_id": ObjectId(pk)})
        except Exception as e:
            logger.exception(
                f"get {pk=}, {sensor_type} failed with exception: {e}"
            )
            return BaseResponse(msg=str(e), status_code=HTTP_404_NOT_FOUND)
        return BaseResponse(data=bson_to_dict(data))
