from typing import Optional, Tuple

from customer.services.customer_service import CustomerService
from mongoengine import Q
from sites.services.site_service import SiteService
from user_management.models.user import CloudUser

from common.const import ROLE_DICT, RoleLevel
from common.framework.service import BaseService
from common.utils import get_objects_pagination


class UserService(BaseService):
    def __init__(self, user: CloudUser):
        self.user = user

    @classmethod
    def create_user(cls, user_data: dict) -> CloudUser:
        role_level = user_data["role_level"]
        if role_level == RoleLevel.CLIENT_SUPER_ADMIN.value:
            user_data["customer"] = CustomerService.named_all_customer_id()
            user_data["sites"] = [SiteService.named_all_site_id()]
        elif role_level == RoleLevel.ADMIN.value:
            user_data["sites"] = [SiteService.named_all_site_id()]
        user = CloudUser(
            username=user_data["username"],
            password=user_data["password"],
            customer=user_data.get("customer"),
            sites=user_data.get("sites"),
            phone=user_data.get("phone", ""),
            email=user_data["email"],
            role_level=role_level,
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
        query = Q(role_level__gte=self.user.role_level)
        if username:
            query &= Q(username__icontains=username)
        if customer:
            query_customer_ids = [customer]
            if self.user.is_cloud_or_client_super_admin():
                query_customer_ids.append(CustomerService.named_all_customer_id())
            query &= Q(customer__in=query_customer_ids)
        if sites:
            if self.user.is_cloud_or_client_super_admin():
                sites.append(SiteService.named_all_site_id())
            query &= Q(sites__in=sites)
        users = CloudUser.objects.filter(query)
        total = users.count()
        users_by_page = get_objects_pagination(page, limit, users)
        customer_ids = set(users_by_page.values_list("customer"))
        customer_dict = CustomerService.get_customer_id_name_dict(customer_ids)
        user_info = [
            {
                "username": user.username,
                "customer_name": customer_dict.get(user.customer, ""),
                "role_level": ROLE_DICT[user.role_level],
                "status": user.is_active,
                "email": user.email,
                "phone": user.phone,
                "id": str(user.pk),
            }
            for user in users_by_page
        ]
        return total, user_info
