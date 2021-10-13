import logging

from customer.models.customer import Customer
from customer.services.customer_service import CustomerService
from customer.validators.customer_serializers import (
    CustomerCreateSerializer,
    CustomerSerializer,
    DeleteCustomerSerializer,
)
from rest_framework.status import HTTP_201_CREATED

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomersView(BaseView):
    permission_classes = PermissionFactory(
        RoleLevel.CLIENT_SUPER_ADMIN, RoleLevel.CLOUD_SUPER_ADMIN
    )

    def get(self, request):
        """
        get list customers, only cloud/client super admin have access to this view.
        :param request:
        :return:
        """
        user = request.user
        logger.info(f"{user.username} request list customers")
        customers = Customer.objects.all()
        total = customers.count()
        data = [
            {
                "id": str(customer.id),
                "name": customer.name,
                "administrative_division": customer.administrative_division,
            }
            for customer in customers
        ]
        return BaseResponse(data={"total": total, "customers": data})

    def post(self, request):
        """
        create a new customer
        :param request:
        :return:
        """
        user = request.user
        data, _ = self.get_validated_data(CustomerCreateSerializer)
        logger.info(f"{user.username} request create new customer with {data=}")
        customer = CustomerService.create_customer(
            data["name"], data["administrative_division"], data.get("remarks")
        )
        return BaseResponse(data=customer.to_dict(), status_code=HTTP_201_CREATED)


class CustomerView(BaseView):
    permission_classes = (
        PermissionFactory(RoleLevel.CLOUD_SUPER_ADMIN, method_list=("DELETE", "PUT")),
        PermissionFactory(RoleLevel.CLIENT_SUPER_ADMIN, method_list=("DELETE", "PUT")),
    )

    def get(self, request, pk):
        _, context = self.get_validated_data(CustomerSerializer, pk=pk)
        customer = context["customer"]
        return BaseResponse(data=customer.to_dict())

    def delete(self, request, pk):
        _, context = self.get_validated_data(DeleteCustomerSerializer, pk=pk)
        customer = context["customer"]
        logger.info(f"{request.user.username} request delete {customer=}")
        CustomerService.delete_customer(customer)
        return BaseResponse()

    def put(self, request, pk):
        # todo : need specify which field can modify? who can modify who?
        user = request.user
        _, context = self.get_validated_data(CustomerSerializer, pk=pk)
        customer = context["customer"]
        return BaseResponse()
