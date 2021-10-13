import logging
from typing import Union

import rest_framework
from django.contrib.auth.models import AnonymousUser
from redis.exceptions import TimeoutError
from rest_framework.exceptions import ErrorDetail
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from common.framework.response import BaseResponse, ExceptionResponse

logger = logging.getLogger(__name__)


class BaseException(Exception):
    """
    All custom exception should inherit this class.
    """

    status_code = HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg, code=None, data=""):
        self.msg = msg
        self.code = code or self.status_code
        self.data = data

    def __str__(self):
        return "<{}: {} {} {}>".format(
            self.__class__.__name__, self.msg, self.code, self.data
        )

    def __repr__(self):
        return self.__str__()


class APIException(BaseException):
    def __init__(self, *args, **kwargs):
        if kwargs.get("status_code"):
            self.status_code = kwargs.pop("status_code")
        else:
            self.status_code = HTTP_400_BAD_REQUEST
        super().__init__(*args, **kwargs)


class InvalidException(BaseException):
    status_code = HTTP_400_BAD_REQUEST


class ForbiddenException(BaseException):
    status_code = HTTP_403_FORBIDDEN


class NotExistException(BaseException):
    status_code = HTTP_404_NOT_FOUND


class NotAcceptableException(BaseException):
    status_code = HTTP_406_NOT_ACCEPTABLE


class AlreadyExistsException(Exception):
    pass


class RollbackException(Exception):
    pass


def check_detail(detail: Union[ErrorDetail, list, dict], code: str) -> Union[str, bool]:
    """
    use code check ErrorDetail in ValidationError
    return error field name if can find error field
    return True for error exists
    return False for error not exists
    :param detail: error detail
    :param code: error code
    :return:
    """
    if isinstance(detail, list):
        return any(check_detail(_detail, code) for _detail in detail)
    elif isinstance(detail, dict):
        for field, _detail in detail.items():
            if check_detail(_detail, code):
                return field
    else:
        return detail.code == code
    return False


def global_exception_handler(e, context):
    request = context["request"]
    data = request.data
    user = getattr(request, "user", None)
    if user:
        if isinstance(user, AnonymousUser):
            user = str(user)
        else:
            user = str(user.id)
    log_msg = f"{e}, context: {context}, data: {data}, user: {user}"
    if isinstance(e, BaseException):
        logger.warning(log_msg)
        return ExceptionResponse(e)
    elif isinstance(e, rest_framework.exceptions.NotAuthenticated):
        logger.info(log_msg)
        return BaseResponse(
            msg="invalid authentication token",
            code=HTTP_401_UNAUTHORIZED,
            data=e.detail,
            status_code=HTTP_401_UNAUTHORIZED,
        )
    elif isinstance(e, FileNotFoundError):
        return BaseResponse(msg="File Not Found", status_code=HTTP_404_NOT_FOUND)
    elif isinstance(e, rest_framework.exceptions.ValidationError):
        logger.warning(log_msg)
        return BaseResponse(
            msg="Invalid input",
            data=e.detail,
            code=HTTP_400_BAD_REQUEST,
            status_code=HTTP_400_BAD_REQUEST,
        )
    elif isinstance(e, rest_framework.exceptions.PermissionDenied):
        logger.warning(log_msg)
        return BaseResponse(
            msg="No permission",
            data=e.detail,
            code=HTTP_403_FORBIDDEN,
            status_code=HTTP_403_FORBIDDEN,
        )
    elif isinstance(e, TimeoutError):
        return BaseResponse(
            msg="Redis timeout",
            code=HTTP_503_SERVICE_UNAVAILABLE,
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
        )
    elif isinstance(e, rest_framework.exceptions.MethodNotAllowed):
        return BaseResponse(
            msg="Method not allowed",
            data=e.detail,
            code=HTTP_405_METHOD_NOT_ALLOWED,
            status_code=HTTP_405_METHOD_NOT_ALLOWED,
        )
    elif isinstance(e, rest_framework.exceptions.ParseError):
        return BaseResponse(
            msg="Invalid input",
            data=e.detail,
            code=HTTP_400_BAD_REQUEST,
            status_code=HTTP_400_BAD_REQUEST,
        )

    logger.exception(log_msg)
    c = HTTP_500_INTERNAL_SERVER_ERROR
    return BaseResponse(msg="internal server error", code=c, status_code=c)
