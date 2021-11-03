from common.framework.view import BaseView
from file_management.validators.navigation_tree_serializers import FileTreeSerializer


class FileNavigationTreeView(BaseView):

    def get(self, request, customer_id):
        user = request.user
        data, context = self.get_validated_data(FileTreeSerializer, customer_id=customer_id)
        customer = context["customer"]
        is_all_customer = context["is_all_customer"]

        pass
