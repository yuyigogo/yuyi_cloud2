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
        user = CloudUser(**user_data)
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
        query = Q()
        if username:
            query &= Q(username__icontains=username)
        if customer:
            if customer == ALL and sites == [ALL]:
                query &= Q(role_level__gte=self.user.role_level)
            elif customer == ALL and sites != [ALL]:
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
        customers = set(users_by_page.values_list("customer"))
        customer_dict = {}
        user_info = [
            {
                "username": user.username,
                "customer": customer_dict.get(str(user.customer), ""),
                "role_level": user.role_level,
                "status": user.is_active,
                "email": user.email,
                "phone": user.phone,
            }
            for user in users_by_page
        ]
        return total, user_info
