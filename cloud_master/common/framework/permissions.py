from common.const import RoleLevel


class PermissionFactory:
    """
    replacement of user.views.has_permission
    use in class which inherit from BaseView

    eg:
    class SomeView(BaseView):
        permission_classes = (
            PermissionFactory(RoleLevel.SUPER_ADMIN.value),
            PermissionFactory(RoleLevel.ADMIN.value),
        )
    """

    def __new__(cls, *init_perm_list, method_list=None):
        class _PermissionClass:
            def has_permission(self, request, view):
                if method_list and request.method not in method_list:
                    return True
                if request.user and request.user.is_authenticated:
                    requested_permissions = (
                        RoleLevel.CLOUD_SUPER_ADMIN.value,
                    ) + init_perm_list
                    return request.user.has_permissions(requested_permissions)
                return False

        return _PermissionClass
