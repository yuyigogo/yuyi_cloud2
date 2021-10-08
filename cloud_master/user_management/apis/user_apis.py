from rest_framework.permissions import AllowAny

from common.framework.view import BaseView


class LoginView(BaseView):
    permission_classes = (AllowAny,)

    def post(self, request):
        pass
