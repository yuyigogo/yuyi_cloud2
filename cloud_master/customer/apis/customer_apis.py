import logging

from customer.models.customer import Customer
from customer.services.customer_service import CustomerService
from customer.validators.customer_serializers import (
    CustomerCreateSerializer,
    CustomerSerializer,
    DeleteCustomerSerializer,
    UpdateCustomerSerializer,
)
from rest_framework.status import HTTP_201_CREATED

from common.const import RoleLevel
from common.framework.permissions import PermissionFactory
from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class CustomersView(BaseView):
    permission_classes = (
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("POST",),
        ),
    )

    def get(self, request):
        user = request.user
        logger.info(f"{user.username} request list customers")
        if user.is_cloud_or_client_super_admin():
            customers = Customer.objects.filter(
                id__ne=CustomerService.named_all_customer_id()
            )
        else:
            customers = Customer.objects.filter(id=user.customer)
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
        PermissionFactory(
            RoleLevel.CLIENT_SUPER_ADMIN.value,
            RoleLevel.CLOUD_SUPER_ADMIN.value,
            method_list=("DELETE", "PUT"),
        ),
    )

    def get(self, request, pk):
        data, _ = self.get_validated_data(CustomerSerializer, pk=pk)
        customer = data["customer"]
        return BaseResponse(data=customer.to_dict())

    def delete(self, request, pk):
        data, _ = self.get_validated_data(DeleteCustomerSerializer, pk=pk)
        clear_resource = data["clear_resource"]
        customer = data["customer"]
        logger.info(f"{request.user.username} request delete {customer=}")
        CustomerService.delete_customer(customer, clear_resource)
        return BaseResponse()

    def put(self, request, pk):
        user = request.user
        data, _ = self.get_validated_data(UpdateCustomerSerializer, pk=pk)
        logger.info(f"{user.username} request update customer: {pk} with {data=}")
        customer = data["customer"]
        name = data.get("name")
        administrative_division = data.get("administrative_division")
        remarks = data.get("remarks")
        update_fields = {}
        if name:
            update_fields["name"] = name
        if administrative_division:
            update_fields["administrative_division"] = administrative_division
        if remarks:
            update_fields["remarks"] = remarks
        if update_fields:
            customer.update(**update_fields)
        return BaseResponse(data=update_fields)
