from django.conf import settings
from mongoengine.base import TopLevelDocumentMetaclass
from mongoengine.queryset import QuerySetManager
from mongoengine.queryset.queryset import QuerySet

from common.framework.db_operate_counter import increase_db_operate_count


class CloudQuerySet(QuerySet):
    def __init__(self, document, collection):
        return super().__init__(document, collection)

    def __call__(self, q_obj=None, **query):
        qs = super().__call__(q_obj, **query)
        if settings.DEBUG is False:
            increase_db_operate_count()
        return qs

    def circular_slice_update(self, limit=100, **kwargs) -> None:
        for i in range(0, self.count(), limit):
            update_query_set = self[i : i + limit]
            update_ids = update_query_set.values_list("id")
            update_query_set.filter(id__in=update_ids).update(**kwargs)

    def scalar(self, *fields):
        """
        default scalar method in QuerySet is too slowly when data count is large.
        because it will been `self._document._from_son` before `_get_scalar`
        here override scalar, and use `as_pymongo` to return dict result.
        and parse dict data to `values_list` style data in `__next__` method
        when _as_pymongo and _scalar both are true.
        """
        if not fields:
            return super().scalar(*fields)
        else:
            queryset = self.clone()
            queryset._scalar = list(fields)
            queryset = queryset.only(*fields).as_pymongo()
            return queryset

    def __next__(self):
        value = super(CloudQuerySet, self).__next__()
        if self._as_pymongo and self._scalar:
            values = [self._parse_scalar_field(field, value) for field in self._scalar]
            if len(self._scalar) == 1:
                return values[0]
            return values
        return value

    def _parse_scalar_field(self, field_name, data):
        db_field_name = self._document._db_field_map.get(field_name, field_name)
        field = self._document._fields.get(field_name)
        value = data.get(db_field_name, None)
        if field and value is not None:
            return field.to_python(value)
        return value


class CloudQuerySetManager(QuerySetManager):
    def __get__(self, instance, owner):
        owner._meta["queryset_class"] = CloudQuerySet
        return super().__get__(instance, owner)


class CloudDocumentMetaclass(TopLevelDocumentMetaclass):
    def __new__(cls, name, bases, attrs):
        attrs["objects"] = CloudQuerySetManager()
        return super().__new__(cls, name, bases, attrs)


def get_queryset_group_fields(queryset: CloudQuerySet, field: str) -> list:
    """
    :param queryset:
    :param field:
    :return:
    """
    if queryset._none:
        # If queryset is XXModel.objects.none(),  can't get the desired results.
        # Even though the XXModel.objects.none().count() is 0, but
        # XXModel.objects.none().aggregate({"$group": {"_id": f"${field}"}} is not [].
        # Execute XXModel.objects.none().aggregate({"$group": {"_id": f"${field}"}} the same to
        # XXModel.objects().aggregate({"$group": {"_id": f"${field}"}}, it will get the full collection data and not [].
        # so, special handling this case.
        return []
    return [
        d["_id"]
        for d in queryset.aggregate({"$group": {"_id": f"${field}"}})
        if d["_id"] is not None
    ]


def get_model_data_by_field_in(
    model, field: str, values: list, select_fields: list,
) -> list:
    """
    :param model:
    :param field:
    :param values:
    :param select_fields:
    :return:
    """
    return get_model_data_by_field_match(model, select_fields, {field: {"$in": values}})


def get_model_data_by_field_match(model, select_fields: list, match: dict,) -> list:
    """
    :param model:
    :param select_fields:
    :param match:
    :return:
    """
    pk_query = match.pop("id", {})
    if pk_query:
        match.update({"_id": pk_query})
    select_fields.append("_id")
    aggregation = [
        {"$match": match},
        {"$project": {field: 1 for field in select_fields}},
    ]

    return [
        {select_field: queryset_one.get(select_field) for select_field in select_fields}
        for queryset_one in model.objects.aggregate(*aggregation)
    ]


def get_distinct_count(model: CloudQuerySet, field: str) -> int:
    distinct_set = set(model.distinct(field))
    distinct_set.discard(None)
    return len(distinct_set)


def get_distinct_exclude_none(model: CloudQuerySet, field: str) -> set:
    field_group_set = set(model.distinct(field))
    field_group_set.discard(None)
    return field_group_set
