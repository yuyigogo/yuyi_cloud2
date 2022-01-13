from typing import Optional, Union

from bson import ObjectId
from customer.models.customer import Customer
from equipment_management.models.gateway import GateWay
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from sites.models.site import Site
from user_management.models.user import CloudUser

from common.const import ALL
from common.framework.service import BaseService


class CustomerService(BaseService):
    @classmethod
    def create_customer(
        cls, name: str, administrative_division: str, remarks: Optional[str] = None
    ) -> Customer:
        customer = Customer(
            name=name, administrative_division=administrative_division, remarks=remarks
        )
        customer.save()
        return customer

    @classmethod
    def delete_customer(cls, customer: Customer, clear_resource: bool):
        # when delete customer, will delete the resources in this customer
        customer_id = customer.pk
        CloudUser.objects.filter(customer=customer_id).delete()
        GateWay.objects.filter(customer=customer_id).delete()
        sites = Site.objects.filter(customer=customer_id)
        site_ids = sites.values_list("id")
        equipments = ElectricalEquipment.objects.filter(site_id__in=site_ids)
        equipment_ids = equipments.values_list("id")
        points = MeasurePoint.objects.filter(equipment_id__in=equipment_ids)
        # clear points and sensor data
        cls.delete_points(points, clear_resource=clear_resource)
        sites.delete()
        equipments.delete()
        customer.delete()

    @classmethod
    def named_all_customer(cls):
        return Customer.objects.get(name=ALL)

    @classmethod
    def get_customer_id_name_dict(cls, customer_ids: Union[set, list]) -> dict:
        return dict(
            Customer.objects.filter(id__in=customer_ids).values_list("id", "name")
        )

    @classmethod
    def get_customer_info(cls, customer_id: Union[str, ObjectId]) -> dict:
        customer = Customer.objects.get(id=customer_id)
        return {
            "id": str(customer.id),
            "name": customer.name,
            "administrative_division": customer.administrative_division,
            "remarks": customer.remarks,
        }
