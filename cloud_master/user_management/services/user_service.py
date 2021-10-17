from typing import Optional, Tuple

from mongoengine import Q
from user_management.models.user import CloudUser

from common.const import ALL
from common.framework.service import BaseService
from common.utils import get_objects_pagination


class UserService(BaseService):
    def __init__(self, user: CloudUser):
        self.user = user

    @classmethod
    def create_user(cls, user_data: dict) -> CloudUser:
        user = CloudUser(
            username=user_data["username"],
            password=user_data["password"],
            customer=user_data["customer"],
            sites=user_data["sites"],
            phone=user_data.get("phone", ""),
            email=user_data["email"],
            role_level=user_data["role_level"],
        )
        user.save()
        return user

    def get_users(
        self,
        page: int,
        limit: int,
        username: Optional[str] = None,
        customer: Optional[str] = None,
        sites: Optional[list] = None,
    ) -> Tuple[int, list]:
        from customer.services.customer_service import CustomerService
        from sites.services.site_service import SiteService

        query = Q()
        if username:
            query &= Q(username__icontains=username)
        if customer:
            named_all_customer_id = str(CustomerService.named_all_customer().id)
            named_all_site_id = str(SiteService.named_all_site().id)
            if customer == named_all_customer_id and sites == [named_all_site_id]:
                # customer and site both are ALL
                query &= Q(role_level__gte=self.user.role_level)
            elif customer == named_all_customer_id and sites != [named_all_site_id]:
                # only customer is ALL
                query &= Q(sites__in=sites)
            else:
                query &= Q(customer=customer, sites__in=sites)
        else:
            # default query or no customer and sites query
            if self.user.is_cloud_or_client_super_admin():
                query &= Q(role_level__gte=self.user.role_level)
            else:
                query &= Q(customer=self.user.customer, sites__in=self.user.sites)

        users = CloudUser.objects.filter(query)
        total = users.count()
        users_by_page = get_objects_pagination(page, limit, users)
        customer_ids = set(users_by_page.values_list("customer"))
        customer_dict = CustomerService.get_customer_id_name_dict(customer_ids)
        user_info = [
            {
                "username": user.username,
                "customer": customer_dict.get(str(user.customer), ""),
                "role_level": user.role_level,
                "status": user.is_active,
                "email": user.email,
                "phone": user.phone,
                "is_active": user.is_active,
            }
            for user in users_by_page
        ]
        return total, user_info
