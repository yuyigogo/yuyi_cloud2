import logging
from typing import Callable

import after_response
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class ValidateMixin(object):
    def get_validated_data(self, serializer_class=None, **extra_data):
        serializer_class = serializer_class or self.serializer_class
        context = {"request": self.request}
        if extra_data:
            context.update(extra_data)
        serializer = serializer_class(
            data=self.request.data or self.request.query_params, context=context
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data, serializer.context


class BaseView(ValidateMixin, APIView):
    """
    All custom class view should inherit this class.

    the custom methods execution sequence are:
    before_action (override if needed)
        |
    before_get/post/put/delete (if existed)
        |
    get/post/put/delete
        |
    after_get/post/put/delete (if existed)
        |
    after_action (override if needed)
    None of these methods can break the sequence except raise a Exception.
    """

    # authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        super(BaseView).__init__(**kwargs)
        self.object = None

    def initial(self, request, *args, **kwargs):
        """
        inject before_action for subclass
        """
        result = super().initial(request, *args, **kwargs)
        content_length = int(self.request.META.get("CONTENT_LENGTH") or 0)
        logger.debug(f"body content length {content_length}")
        self.before_action(request, *args, **kwargs)
        return result

    def finalize_response(self, request, response, *args, **kwargs):
        """
        inject after_action for subclass
        """
        self.after_action(request, response, *args, **kwargs)
        return super().finalize_response(request, response, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?
        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(
                    self, request.method.lower(), self.http_method_not_allowed
                )
                before_handler = getattr(
                    self, "%s%s" % ("before_", request.method.lower()), False
                )
                after_handler = getattr(
                    self, "%s%s" % ("after_", request.method.lower()), False
                )
            else:
                handler = self.http_method_not_allowed

            if before_handler:
                before_handler(request, *args, **kwargs)
            response = handler(request, *args, **kwargs)
            if after_handler:
                after_handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    def before_action(self, request, *args, **kwargs):
        pass

    def after_action(self, request, response, *args, **kwargs):
        pass

    def permission_denied(self, request, message=None):
        if request.authenticators and not request.successful_authenticator:
            raise NotAuthenticated()
        raise PermissionDenied(detail=message)

    @staticmethod
    def after_response_run(func: Callable, *args, **kwargs):
        """
        Simple asynchronous execution.
        It will execute code after the request is complete, without the need for additional daemons or task queues.
        :param func: asynchronous function
        :param args: asynchronous function args
        :param kwargs: asynchronous function kwargs
        :return: asynchronous function result
        Usage::
            >>> import after_response
            >>> @after_response.enable
            >>> def after_response_func(args):
            >>>     pass
            >>> after_response_func.after_response("args")
        """
        return after_response.enable(func).after_response(*args, **kwargs)
