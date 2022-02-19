from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView
from file_management.services.excel_service import ExcelService
from file_management.validators.excel_file_serializers import ExcelImportSerializer


class ImportFileView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value, RoleLevel.CLOUD_SUPER_ADMIN.value,
        ),
    )

    def post(self, request):
        data, _ = self.get_validated_data(ExcelImportSerializer)
        ExcelService.file_import(excel_file=data["file"])
        return BaseResponse()
