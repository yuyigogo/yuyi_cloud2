from collections import defaultdict

from common.framework.service import BaseService
from customer.models.customer import Customer
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from sites.models.site import Site


class FileNavigationService(BaseService):
    @classmethod
    def get_file_navigation_tree_by_customer(cls, customer: Customer) -> list:
        sites = Site.objects.only("name").filter(customer=customer.pk)
        site_info = dict(sites.valuse_list("id", "name"))
        site_ids = site_info.keys()
        equipments = ElectricalEquipment.objects(site_id__in=site_ids).only(
            "device_name"
        )
        equipment_info = defaultdict(list)
        equipment_ids = []
        for e in equipments:
            equipment_ids.append(e.pk)
            equipment_info[str(e.site_id)].append(
                {"name": e.device_name, "id": str(e.pk), "children": []}
            )
        points = MeasurePoint.objects(equipment_id__in=equipment_ids).only(
            "measure_name"
        )
        point_info = defaultdict(list)
        for p in points:
            point_info[str(p.equipment_id)].append({"id": str(p.pk), "name": p.measure_name})

        tree_list = []
        tree_dict = {"id": "", "name": "", "children": []}
        for site_id, site_name in site_info.items():
            tree_dict["id"] = str(site_id)
            tree_dict["name"] = site_name
            equipment_list = equipment_info.get(str(site_id), [])
            tree_dict["children"] = equipment_list
            for equipment_dict in equipment_list:
                for equipment_id, equipment_name in equipment_dict.items():
                    point_list = point_info.get(equipment_id, [])
                    equipment_dict["children"] = point_list
            tree_list.append(tree_dict)
        return tree_list
