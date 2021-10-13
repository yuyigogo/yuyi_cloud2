import logging

from customer.services.customer_service import CustomerService
from customer.validators.customer_serializers import CustomerCreateSerializer
from rest_framework.status import HTTP_201_CREATED

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomersView(BaseView):
    permission_classes = PermissionFactory(
        RoleLevel.CLIENT_SUPER_ADMIN, RoleLevel.CLOUD_SUPER_ADMIN, method_list=("POST",)
    )

    def post(self, request):
        user = request.user
        data, _ = self.get_validated_data(CustomerCreateSerializer)
        logger.info(f"{user.username} request create new customer with {data=}")
        customer = CustomerService.create_customer(
            data["name"], data["administrative_division"], data.get("remarks")
        )
        return BaseResponse(data=customer.to_dict(), status_code=HTTP_201_CREATED)
