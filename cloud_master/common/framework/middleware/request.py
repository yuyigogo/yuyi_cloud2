import json
import logging
import threading
import traceback

from dicttoxml import dicttoxml
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from rest_framework.status import HTTP_400_BAD_REQUEST

from common.utils import MiddlewareMixin, xml_to_dict

logger = logging.getLogger(__name__)
threading_local = threading.local()


class DisableCsrfCheck(MiddlewareMixin):
    """
    Middleware that disable the csrf check.
    This should be used only in dev environment.
    """

    def process_request(self, req):
        attr = "_dont_enforce_csrf_checks"
        if not getattr(req, attr, False):
            setattr(req, attr, True)


class DBOperateCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.m = __import__(
            "common.framework.db_operate_counter",
            globals(),
            locals(),
            ["db_operate_counter"],
        )

    def __call__(self, request):
        self.m.reset_db_operate_counter()
        response = self.get_response(request)
        if self.m.g_db_operate_count:
            logger.debug(
                f"{request.path} db operate count is {self.m.g_db_operate_count}"
            )
        return response


class XmlResponse(HttpResponse):
    @classmethod
    def success_xml_response(cls, response):
        try:
            response_xml = dicttoxml(
                json.loads(response.content.decode("utf-8")),
                root=True,
                attr_type=True,
                item_func=lambda x: x,
            )
            return HttpResponse(response_xml, content_type="application/xml")
        except Exception as e:
            logger.error(e)
            return cls.error_xml_response("Other error, please contact administrator.")

    @staticmethod
    def error_xml_response(msg):
        response_xml = dicttoxml(
            {"msg": msg, "data": {}, "code": HTTP_400_BAD_REQUEST},
            root=True,
            attr_type=True,
        )
        return HttpResponse(
            response_xml, status=HTTP_400_BAD_REQUEST, content_type="application/xml",
        )

    @classmethod
    def check_content_type(cls, request):
        if request.META.get("CONTENT_TYPE") == "application/xml":
            try:
                request.META["CONTENT_TYPE"] = "application/json"
                new_body = cls.xml_body(request.body)
                request._body = new_body
            except ValidationError as e:
                logger.warning(e.message)
                return XmlResponse.error_xml_response(e.message)
            except Exception as e:
                logger.warning(e)
                return XmlResponse.error_xml_response(str(e))

    @staticmethod
    def xml_body(body):
        xml_str = body.decode("utf-8")
        body_dict = xml_to_dict(xml_str, root=False, item_func=lambda x: x)
        ret_xml_body = json.dumps(body_dict).encode("utf-8")
        return ret_xml_body


class GlobalRequestMiddleware(MiddlewareMixin):
    """
    Middleware used give value for threading_local
    """

    @staticmethod
    def process_request(request):
        threading_local.request = request
        threading_local.body = request.body
        request.source_content_type = request.META.get("CONTENT_TYPE")
        return XmlResponse.check_content_type(request)

    @staticmethod
    def process_response(request, response):
        if request.source_content_type == "application/xml":
            return XmlResponse.success_xml_response(response)
        return response


class GlobalRequest(object):
    def __getattr__(self, item):
        return getattr(getattr(threading_local, "request", None), item, None)

    @staticmethod
    def get_data():
        request = threading_local.request
        request_data = getattr(request, "data", None)
        if not request_data:
            try:
                request_data = {k: v[0] for k, v in dict(request.GET).items()}
                update_dict = (
                    json.loads(request.body) if hasattr(request, "body") else {}
                )
                request_data.update(update_dict)
            except Exception as e:
                logger.warning(e)
                logger.warning(traceback.format_exc())
                request_data = {}
            finally:
                threading_local.request.data = request_data
        return request_data


global_request = GlobalRequest()
