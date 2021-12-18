import logging
from datetime import datetime

import pytz
from bson.objectid import ObjectId
from django.conf import settings
from mongoengine.base.fields import ObjectIdField
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import BooleanField, DateTimeField, EmailField, StringField

from common.framework.db_operate_counter import increase_db_operate_count
from common.framework.queryset import CloudDocumentMetaclass
from common.utils.datetime_utils import date_to_timestamp

logger = logging.getLogger(__name__)


class DocumentMixin(object):
    @staticmethod
    def formalize_id(id):
        """
        formalize an id(str or dict) to an ObjectId() object
        support two types of given id:
            1: str: "xxxxxxxx"
            2: dict: {"$oid": "xxxxxxxx"}, this is format returned by to_json()

        :param id: id in str or dict format
        :return: an ObjectId() object
        """
        if isinstance(id, dict):
            id = ObjectId(id["$oid"])
        elif isinstance(id, str):
            id = ObjectId(id)
        return id

    def to_dict(self):
        bson = self.to_mongo()
        return bson_to_dict(dict(bson))

    @property
    def fields_ordered(self) -> tuple:
        """Model fields"""
        return self._fields_ordered


class CloudDocument(Document, DocumentMixin, metaclass=CloudDocumentMetaclass):
    """
    basic structure of a ginerativ document with the custom fields that will be
    part of every document in the mongo db database
    """

    meta = {"abstract": True, "strict": False}

    # create date
    create_date = DateTimeField(default=lambda: datetime.now())
    # update date
    update_date = DateTimeField(default=lambda: datetime.now())
    # the version of the structure of the mongo document
    version_structure = StringField(max_length=100, default="1")

    def save(self, *args, auto_update_update_date=True, **kwargs):
        if settings.DEBUG is True:
            increase_db_operate_count()
        changed_fields = self._get_changed_fields()
        if (
            auto_update_update_date
            and changed_fields
            and "update_date" not in changed_fields
        ):
            self.update_date = self._default_update_date
        return super(CloudDocument, self).save(*args, **kwargs)

    def update(self, auto_update_update_date=True, **kwargs):
        if auto_update_update_date and kwargs:
            self.update_date = kwargs.get("update_date", self._default_update_date)
            kwargs.update({"update_date": self.update_date})
        super(CloudDocument, self).update(**kwargs)

    @property
    def _default_update_date(self):
        return datetime.now(tz=pytz.utc)

    @classmethod
    def _get_collection(cls):
        return super()._get_collection()

    @classmethod
    def get_fields(cls, type):
        """
        filter fields by field type

        :param type: field type: for example, ObjectIdField
        :return: list of fields filtered
        """
        return [name for name, field in cls._fields.items() if isinstance(field, type)]

    @classmethod
    def formalize_ids(cls, obj_dict):
        """
        formalize all the ids fields: cast value of ObjectIdField to ObjectId object

        :param obj_dict: dict representation of an object
        :return:
        """
        obj_id_fields = cls.get_fields(ObjectIdField)
        for field, value in obj_dict.items():
            if value and field in obj_id_fields:
                obj_dict[field] = cls.formalize_id(value)

    def delete(self, detach_it_from_dependencies=True, **write_concern):
        super(CloudDocument, self).delete(**write_concern)

    @classmethod
    def query_exclude_sys_fields(cls, query):
        """
        effect query excluding system fields for a better performance, this could be extremely useful when querying
        a list of objects.
        list of system fields: 'create_user_id', 'update_user_id', 'update_date', 'linked_objects', 'version_structure'

        :param query: Query object
        :return: QuerySet object
        """
        return cls.objects(query).exclude(
            "create_user_id", "update_user_id", "update_date", "version_structure"
        )

    def update_from_another_instance(self, instance):
        for field in instance._fields:
            self[field] = instance[field]
        self.save()

    @property
    def update_date_timestamp(self):
        return int(self.update_date.timestamp())


def bson_to_dict(bson):
    if isinstance(bson, dict):
        return {bson_to_dict(k): bson_to_dict(v) for k, v in bson.items()}
    elif isinstance(bson, list):
        return list(map(bson_to_dict, bson))
    elif isinstance(bson, (str, int, bool)):
        return bson
    elif bson is None:
        return bson
    else:
        if hasattr(bson, "to_json"):
            return bson.to_json()
        return str(bson)


class CloudEmbeddedDocument(EmbeddedDocument, DocumentMixin):
    """
    basic structure of a cloud embedded document with the custom fields that
    will be part of every embedded document in the mongo db database
    """

    id = ObjectIdField()
    update_date = DateTimeField(default=lambda: datetime.now(tz=pytz.utc))

    meta = {"abstract": True, "strict": False}

    def save(self):
        if self._instance:
            self._instance.save()

    @property
    def update_date_timestamp(self) -> int:
        return date_to_timestamp(self.update_date)


class AllowBlankEmailField(EmailField):
    def validate(self, value):
        if value != "":
            return super().validate(value)


class AccessForbiddenException(Exception):
    def __str__(self):
        return "access forbidden"


class NullableObjectIdField(ObjectIdField):
    def prepare_query_value(self, op, value):
        if value is None:
            return value
        return super().prepare_query_value(op, value)
