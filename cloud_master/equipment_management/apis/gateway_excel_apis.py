"""
1. 网关档案导入
2. 网关档案导出

    网关档案导入：模板只需要公司/站点名；
                校验：公司/站点是否存在；request.user 是否有改公司/站点的权限；
                     client_number是否已绑定
"""
import logging
from datetime import datetime

from django.http import HttpResponse
from equipment_management.services.gateway_export_service import GatewayExportService
from equipment_management.services.gateway_import_service import GatewayExcelService
from equipment_management.validators.gateway_import_export_serializers import (
    GatewayExportSerializer,
    GatewayImportSerializer,
)

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView
from common.utils.str_utils import to_ascii

logger = logging.getLogger(__name__)


class GatewayImportView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            RoleLevel.ADMIN.value,
        ),
    )

    def post(self, request):
        data, _ = self.get_validated_data(GatewayImportSerializer)
        logger.info(f"{request.user} request import gateway from excel!")
        validate_customer_id = data["validate_customer_id"]
        service = GatewayExcelService(validate_customer_id=validate_customer_id)
        import_succeed_num = service.gateway_file_import(data["file"])
        return BaseResponse(data={"import_succeed_num": import_succeed_num})


class GatewayExportView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            RoleLevel.ADMIN.value,
        ),
    )

    def get(self, request):
        data, _ = self.get_validated_data(GatewayExportSerializer)
        user = request.user
        logger.info(f"{user} request export gateways with {data=}!")
        gateway_export_service = GatewayExportService(
            user, data["customer_id"], site_id=data.get("site_id")
        )
        content = gateway_export_service.get_excel_content()
        now = datetime.now()
        filename = f"云平台设备档案-{now.strftime('%d%m%Y')}.xlsx"
        disposition = f"attachment; filename={to_ascii(filename)}"
        response = HttpResponse(content, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = disposition
        return response
