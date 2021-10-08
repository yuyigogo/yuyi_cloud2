from common.utils import MiddlewareMixin


class TokenHandlerMiddleware(MiddlewareMixin):
    """
    Middleware responsible  for setting and re-emitting the token
    to the authenticated user
    """

    @staticmethod
    def process_response(request, response):
        token_key = request.META.get("HTTP_X_AUTH_TOKEN")
        if token_key:
            response.set_cookie("cloud_token", token_key)

        return response
