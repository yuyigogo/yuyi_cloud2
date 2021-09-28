"""
The office document about validation is here:
https://www.django-rest-framework.org/api-guide/serializers/#validation

"""
from typing import Callable, List, Union

from bson import ObjectId
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer


class BaseSerializer(Serializer):
    """
    All custom Serializer should inherit this class.
    """

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate(self, data):
        """
        To do any other validation after the base validation.
        the extra data which pass from get_validated_data can be get in this way:
        self.context["extra_data_field_name"]
        Also, if you want to cache something while validating, just put in context:
        self.context["key"] = something_need_to_be_cache
        Then the context will return by get_validated_data
        """
        return data

    @staticmethod
    def check_object_id(data_id: str) -> bool:
        if not ObjectId.is_valid(data_id):
            raise ValidationError(f"{data_id} is not a ObjectId!")
        return True

    @classmethod
    def check_and_change_ids_to_object_ids(
        cls, value: List[Union[str, ObjectId]]
    ) -> List[ObjectId]:
        """
        :param value:
        :return:
        """
        obj_ids = [ObjectId(obj_id) for obj_id in value if cls.check_object_id(obj_id)]
        return obj_ids


def validate_and_save_data_list(data_list, get_validated_serializer):
    # type: (List[dict], Callable[[dict], Serializer]) -> list
    """
    validate and save every data in a data list
    :param data_list: data list
    :param get_validated_serializer: parse data to validated serializer
    :return:
    """
    serializer_list = []
    error_detail = {}
    for index, data in enumerate(data_list):
        try:
            serializer = get_validated_serializer(data)
            serializer_list.append(serializer)
        except ValidationError as e:
            error_detail[str(index)] = e.detail
    if error_detail:
        raise ValidationError(error_detail)
    instance_list = []
    for serializer in serializer_list:
        instance = serializer.save()
        instance_list.append(instance)

    return instance_list
