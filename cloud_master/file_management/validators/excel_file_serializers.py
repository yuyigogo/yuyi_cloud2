from rest_framework.fields import FileField

from common.framework.serializer import BaseSerializer


class ExcelImportSerializer(BaseSerializer):
    file = FileField(required=True, allow_empty_file=False)
