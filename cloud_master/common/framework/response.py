from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


class BaseResponse(Response):
    """
    All custom response should inherit this class.
    """

    def __init__(self, msg="", code=0, data=None, status_code=HTTP_200_OK):
        data = {"msg": msg, "code": code, "data": data}
        super().__init__(data=data, content_type="application/json", status=status_code)


class ExceptionResponse(BaseResponse):
    def __init__(self, e):
        super().__init__(e.msg, e.code, e.data, e.status_code)
