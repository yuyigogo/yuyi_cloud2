import logging

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomersView(BaseView):
    permission_classes = PermissionFactory(
        RoleLevel.CLIENT_SUPER_ADMIN, RoleLevel.CLOUD_SUPER_ADMIN, method_list=("POST",)
    )

    def post(self, request):
        pass
