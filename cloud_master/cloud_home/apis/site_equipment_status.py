import logging

from common.framework.view import BaseView
logger = logging.getLogger(__name__)


class SitesStatusView(BaseView):
    def get(self, request, customer_id):
        pass


class EquipmentsStatusView(BaseView):
    def get(self, request, site_id):
        pass
