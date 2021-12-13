from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.view import BaseView


class ImportFileView(BaseView):
    permission_classes = (PermissionFactory(RoleLevel.CLOUD_SUPER_ADMIN.value,),)

    def post(self, request):
        pass
