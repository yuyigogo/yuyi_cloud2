import logging

from file_management.services.file_navigation_service import FileNavigationService
from file_management.validators.navigation_tree_serializers import FileTreeSerializer

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class FileNavigationTreeView(BaseView):
    def get(self, request, customer_id):
        user = request.user
        data, context = self.get_validated_data(
            FileTreeSerializer, customer_id=customer_id
        )
        logger.info(f"{user.username} request file tree data for {customer_id=}")
        customer = context["customer"]
        file_tree = FileNavigationService.get_file_navigation_tree_by_customer(customer)
        return BaseResponse(data=file_tree)


class AllFileNavigationTreeView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value, RoleLevel.CLOUD_SUPER_ADMIN.value,
        ),
    )

    def get(self, request):
        # todo
        pass
