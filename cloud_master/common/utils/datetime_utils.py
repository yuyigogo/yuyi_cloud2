import json
import logging
import re
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Union

import pytz
from babel.dates import format_datetime
from bson.json_util import dumps
from django.utils.translation import get_language

from common.const import BaseEnum


class DateUnit(str, BaseEnum):
    day = "day"
    month = "month"
    year = "year"


def datetime_to_timestamp_dict(datetime_obj):
    """
    this is used to convert a datetime object to a dict like: {$oid: timestamp}.
    :param datetime_obj: a datetime object
    :return:
    """
    return json.loads(dumps(datetime_obj))


def utc_datetime_to_local_datetime(datetime, timezone_str):
    """
    :param datetime: a Datetime object
    :param timezone_str: timezone in format str, for example, 'Europe/Paris'
    :return:
    """
    utc_datetime = datetime.replace(tzinfo=pytz.utc)
    local_datetime = utc_datetime.astimezone(tz=pytz.timezone(timezone_str))
    return local_datetime


def date_to_iso(date):
    """
    convert a Date Object to "yyyy-mm-dd"
    :param date:
    :return:
    """
    return datetime.strftime(date, "%Y-%m-%d")


def iso_to_mm_dd_yyyy(date):
    """
    convert "yyyy-mm-dd" to "mm/dd/yyyy"
    :param date:
    :return:
    """
    try:
        splits = date.split("-")
        return "/".join([splits[1], splits[2], splits[0]])
    except:
        logging.warning(f"iso_to_mm_dd_yyyy transform date exception. date: {date}")
        return None


def mm_dd_yyyy_to_iso(date):
    """
    convert "mm/dd/yyyy" to "yyyy-mm-dd"
    :param date:
    :return:
    """
    try:
        splits = date.split("/")
        return "-".join([splits[2], splits[0], splits[1]])
    except:
        logging.warning(f"mm_dd_yyyy_to_iso transform date exception. date: {date}")
        return None


def get_date_from_yyyy_mm_dd(date):
    """
    return a Date object from a date string in format_string
    :param date: date string in format yyyy-mm-dd
    :return: Date object
    """
    # Encode characters to byte to strip them of invisibile unicode characters
    # Such as left-to-right mark or right-to-left mark
    # Decode to get the stripped string back
    date_decoded = date.encode("ascii", "ignore").decode("ascii")
    return datetime.strptime(date_decoded, "%Y-%m-%d").date()


def get_date_by_month(date):
    """
    :param date: a string representation of a date with month, year
    :return: the corresponding datetime.date object
    :raises ValueError: if the string format does not correspond to the MM/YYYY format
    """
    return datetime.strptime(date, "%m/%Y").date()


def get_date_from_string(date_string):
    match = re.search(r"\d{4}/\d{2}/\d{2}", date_string)
    match1 = re.search(r"\d{2}/\d{2}/\d{4}", date_string)
    matching = match or match1
    by_month = False
    if not matching:
        match = re.search(r"\d{4}/\d{2}", date_string)
        match1 = re.search(r"\d{2}/\d{4}", date_string)
        matching = match or match1
        by_month = True
    return matching, by_month


def get_date_by_language(date):
    """
    :param date: a string representation of a date with day, month, year
    :return: the corresponding datetime.date object
    :raises ValueError: if the string format does not correspond to the locale format
    """

    # Encode characters to byte to strip them of invisibile unicode characters
    # Such as left-to-right mark or right-to-left mark
    # Decode to get the stripped string back
    date_decoded = date.encode("ascii", "ignore").decode("ascii")
    if get_language() == "fr":
        return datetime.strptime(date_decoded, "%d/%m/%Y").date()
    elif get_language() == "en":
        return datetime.strptime(date_decoded, "%m/%d/%Y").date()
    else:
        return datetime.strptime(date_decoded, "%d/%m/%Y").date()


class DateStringFormat(Enum):
    database_format = "%m/%d/%Y"


def get_string_date_by_language(date):
    """
    returns a string with the date formatted by the language server
    :param date: date string with format mm/dd/yyyy
    :return: a date string formatted by language
    """
    language = get_language()
    if language == "fr":
        date_obj = datetime.strptime(
            date, DateStringFormat.database_format.value
        ).date()
        date = datetime.strftime(date_obj, "%d/%m/%Y")
    return date


def get_simple_datetime_by_language(date_time: datetime, language: str) -> str:
    """
    :param date_time:
    :param language:
    :return:
    >>> get_simple_datetime_by_language(date_time, "en")
    12 Oct. 2020, 03:28(UTC)
    """
    simple_datetime_str = format_datetime(
        date_time, "d MMM. yyyy, HH:mm(z)", tzinfo=pytz.utc, locale=language
    )
    return simple_datetime_str


def is_dst(dt=None, timezone="UTC"):
    """
    :param dt:
    :param timezone:
    :return:
    """
    if dt is None:
        dt = datetime.utcnow()
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(dt, is_dst=None)
    return timezone_aware_date.tzinfo._dst.seconds != 0


def date_to_timestamp(date_time: datetime) -> int:
    return int(date_time.timestamp())


def timestamp_to_date(timestamp: int) -> datetime:
    return datetime.utcfromtimestamp(timestamp)


def now_with_timezone(time_zone: float = 0) -> datetime:
    return datetime.now(timezone(timedelta(hours=time_zone)))


def full_datetime_str(time: datetime) -> str:
    """
    Wednesday, Apr 14, 2021 03:04:28 PM (UTC+08:00)
    """
    return time.strftime("%A, %b %d, %Y %I:%M:%S %p (%Z)")


def timezone_offset_to_timezone(timezone_offset: Union[str, int]) -> float:
    """
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getTimezoneOffset
    The number of minutes returned by getTimezoneOffset() is
    positive if the local time zone is behind UTC,
    and negative if the local time zone is ahead of UTC.
    """
    try:
        return -(int(timezone_offset) / 60)
    except ValueError:
        return 0
