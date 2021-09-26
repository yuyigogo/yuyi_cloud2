import cProfile
import datetime
import hashlib
import json
import math
import os
import pstats
import re
import string
import sys
import traceback
from contextlib import contextmanager
from decimal import Decimal
from functools import partial, wraps
from logging import getLogger
from time import time
from typing import Iterable, Optional, Tuple, Union
from urllib.parse import quote
from xml.etree.ElementTree import fromstring

import pytz
import requests
from babel.dates import format_datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from dicttoxml import default_item_func
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from mongoengine import Q, QuerySet
from unidecode import unidecode

from common.const import (
    DATE_FMT,
    DATE_FORMAT_DICT,
    DATE_FORMAT_EN,
    FORMULA_DATE_FORMAT,
    MONTH_LANG_ABBREVIATION,
)

logger = getLogger(__name__)


class MiddlewareMixin:
    """
    copy from django.utils.deprecation
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
            if response:
                return response
        response = response or self.get_response(request)
        if hasattr(self, "process_response"):
            response = self.process_response(request, response)
        return response


@contextmanager
def time_context(label=""):
    t = time()
    yield
    logger.debug(f"{label} used {time() - t}")


@contextmanager
def profile_context(filename):
    profile = cProfile.Profile()
    profile.enable()
    yield
    profile.disable()
    pstats.Stats(profile).sort_stats("tottime").dump_stats(filename)


def pprof(func=None, *, dumpfile=None):
    """
    The default dump file is `<func.__qualname__>.prof`, if dumpfile is not specified.
    Turn on profile by setting environment variable `PROFILE` or `profile`, such as:

        # export profile=1
        # run server ...
    or
        # profile=1 python manage.py runsslserver 0.0.0.0:8000


    __qualname__:

    >>> class C:
    ...     class D:
    ...         def meth(self):
    ...             pass
    ...
    >>> C.__qualname__
    'C'
    >>> C.D.__qualname__
    'C.D'
    >>> C.D.meth.__qualname__
    'C.D.meth'


    usages:

    the dumpfile of the following code is 'foo.prof'

    >>> @pprof
    ... def foo():
    ...     pass
    ...


    the dumpfile of the following code is 'TestView.get.prof'

    >>> class TestView(BaseView):
    ...
    ...     @pprof
    ...     def get(self):
    ...         pass
    ...


    the dumpfile of the following code is 'TestView.get.prof'

    >>> class TestView(BaseView):
    ...
    ...     @pprof(dumpfile="TestView.get.prof")
    ...     def get(self):
    ...         pass
    ...
    """

    if not callable(func):
        return partial(pprof, dumpfile=dumpfile)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # PROFILE must be `0` or `1`
        enable_profile = int(os.getenv("PROFILE", 0) or os.getenv("profile", 0))
        if enable_profile:
            profile = cProfile.Profile()
            profile.enable()
            exception = None
            try:
                result = func(*args, **kwargs)
            except BaseException as e:
                exception = e
            finally:
                profile.disable()

            output = dumpfile or f"{func.__qualname__}.prof"
            # Sort stat by internal time.
            sortby = "tottime"
            ps = pstats.Stats(profile).sort_stats(sortby)
            ps.dump_stats(output)

            if exception:
                raise exception
        else:
            result = func(*args, **kwargs)
        return result

    return wrapper


def first(items, condition=None):
    return next(
        (item for item in items if ((condition is None) or condition(item))), None
    )


class CacheContext(object):
    def __init__(self):
        self.count = 0
        self.cache = {}

    def __enter__(self):
        self.count += 1
        return self

    def __exit__(self, *exc):
        self.count -= 1
        if self.count == 0:
            self.cache = {}
        return False


def context_cache(func):
    """
    @context_cache
    def double(x):
        return x * 2

    double(1)  # call not with cache
    with double.cache_context:
        double(2)  # call with cache
    double(3)  # call not with cache

    """
    context = CacheContext()

    def wrapper(*args):
        if context.count == 0:
            return func(*args)
        if args not in context.cache:
            context.cache[args] = func(*args)
        return context.cache[args]

    wrapper.cache_context = context

    return wrapper


def get_num_by_string(string):
    p = re.compile(r"\d+")
    num = "".join(p.findall(string))
    return num


def datetime_from_str(date_str):
    try:
        num = get_num_by_string(date_str)[:14]
        ret_date = datetime.datetime.strptime(num, "%Y%m%d%H%M%S")
    except Exception as e:
        ret_date = None
        logger.error(e)
    finally:
        return ret_date


def check_email(mail):
    p = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if p.match(mail):
        return True
    else:
        return False


def get_ding_talk_traceback_msg(update_dict: Optional[dict] = None) -> str:
    """
    :param update_dict:
    :return:
    """
    format_dict = {}
    exc_info = sys.exc_info()
    traceback_data = traceback.extract_tb(exc_info[2])
    if traceback_data:
        source_error = traceback_data[-1]
        format_dict.update(
            {
                "file_name": source_error.filename.split(os.path.sep)[-1],
                "line_no": source_error.lineno,
                "line_info": source_error.line,
                "error_info": exc_info[1],
                "detail": traceback.format_exc(),
            }
        )
    if update_dict:
        format_dict.update(update_dict)
    msg = "\n" + "\n".join(f"- {key}: {value}" for key, value in format_dict.items())
    return msg


def monitor(
    title: str,
    message: str,
    at_mobiles: Union[list, str, None, tuple] = None,
    is_at_all: bool = False,
) -> None:
    """
    ding_talk warning monitor
    :param title:
    :param message:
    :param at_mobiles: @group members by phone numbers.
    :param is_at_all: @all set True, or False.
    :return:
    """
    monitor_url = settings.MONITOR_URL
    if not monitor_url:
        logger.info(
            "MONITOR_URL has no configured value, ding talk message is not be sent."
        )
        return
    at_mobiles = (
        at_mobiles if isinstance(at_mobiles, (list, tuple)) else [str(at_mobiles)]
    )
    msg = {
        "msgtype": "markdown",
        "markdown": {"title": "Drafter backend warning!", "text": ""},
        "at": {"atMobiles": at_mobiles, "isAtAll": is_at_all},
    }
    format_dict = {
        "title": title,
        "message": message,
        "create_time": str(datetime.datetime.utcnow()),
    }
    text = "\n".join(f"- {key}->: {value}" for key, value in format_dict.items())
    msg["markdown"]["text"] = text
    headers = {"Content-Type": "application/json"}
    try:
        requests.post(monitor_url, data=json.dumps(msg), headers=headers, timeout=1)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())


def cast_from_attribute(child, type_attrib):
    """Converts XML text into a Python data format based on the tag attribute"""
    text = child.text
    attr = child.attrib
    if attr[type_attrib] in ("str", "unicode"):
        if text is None:
            return ""
        return str(text)
    elif attr[type_attrib] in ("int", "long"):
        return int(text)
    elif attr[type_attrib] in ("float",):
        return float(text)
    elif attr[type_attrib] in ("number",):
        return Decimal(text)
    elif attr[type_attrib].lower() == "null":
        return None
    elif attr[type_attrib] in ("bool",):
        boole_dict = {"true": True, "false": False}
        return boole_dict.get(str(text).lower())
    elif attr[type_attrib] in ("array", "list", "item"):
        return []
    elif attr[type_attrib] in ("dict",):
        return {}
    else:
        raise ValidationError(
            f"In {child.tag} tag, the {type_attrib}={attr[type_attrib]} is not supported!"
        )


def xml_to_dict(
    xml_str, type_attrib="type", root=True, item_func=default_item_func, parent="root"
):
    """Converts an XML string into a Python object based on each tag's attribute"""

    def add_to_output(obj, child):
        if type_attrib not in child.attrib:  # no type
            raise ValidationError(f"In {child.tag} tag have not {type_attrib}!")
        if isinstance(obj, dict):
            obj.update({child.tag: cast_from_attribute(child, type_attrib)})
            for sub in child:
                add_to_output(obj[child.tag], sub)
        elif isinstance(obj, list):
            obj.append(cast_from_attribute(child, type_attrib))
            for sub in child:
                add_to_output(obj[-1], sub)

    root_data = fromstring(xml_str)
    output = {}
    outputs = []
    item_name = item_func(parent)
    for child_data in root_data:
        add_to_output(output, child_data)
        outputs.append(output.get(item_name, output))
    if item_name in output:  # xml list data
        ret_output = outputs
    else:  # xml dict data
        ret_output = output
    if root:
        return {root_data.tag: ret_output}
    else:
        return ret_output


def get_boolean_result_by_str(
    boolean_str: str, default: Optional[bool] = None
) -> Optional[bool]:
    boolean_dict = {"false": False, "true": True}
    return boolean_dict.get(str(boolean_str).lower(), default)


def get_objects_pagination(page: int, limit: int, model_objects: QuerySet) -> QuerySet:
    start = (page - 1) * limit
    stop = page * limit
    return model_objects[start:stop]


def string_to_utc_time(time_string: str) -> datetime.datetime:
    datetime_struct = parser.parse(time_string, default=datetime.datetime(2020, 1, 1))
    date_time = datetime_struct.astimezone(pytz.utc)
    return date_time


def format_formula_date(date: datetime.datetime) -> str:
    return datetime.datetime.strftime(date, FORMULA_DATE_FORMAT)


def date_string_to_timestamp(date_string: str) -> int:
    return int(string_to_utc_time(date_string).timestamp())


def get_between_date_by_time_string(
    time_string: str,
) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    :param time_string:
    :return:
    """
    timedelta_tuple = (
        relativedelta(years=+1),
        relativedelta(months=+1),
        relativedelta(days=+1),
        relativedelta(hours=+1),
        relativedelta(minutes=+1),
        relativedelta(seconds=+1),
    )
    start_date = string_to_utc_time(time_string)
    split_time_string = (
        time_string.replace("-", "|").replace(":", "|").replace(" ", "|")
    )
    date_length = len(split_time_string.split("|"))
    if date_length <= len(timedelta_tuple):
        delta_time = timedelta_tuple[date_length - 1]
        end_data = start_date + delta_time
    else:
        logger.info(f"{time_string}:{date_length} is too long than  timedelta_tuple")
        end_data = start_date
    return start_date, end_data


def slice_objects_by_page(page: int, limit: int, *objs: QuerySet) -> Tuple[dict]:
    """
    :param page: page num
    :param limit: limit num
    :param objs: QuerySet tuple
    :return: list of QuerySet
    """
    per_page_objs = tuple()
    start = (page - 1) * limit
    stop = page * limit

    for obj in objs:
        if stop <= 0:
            break
        per_page_objs += tuple(obj[start:stop].as_pymongo())
        if len(per_page_objs) >= limit:
            return per_page_objs
        else:
            obj_count = obj.count()
            stop -= obj_count
            start -= obj_count
            start = max(0, start)

    return per_page_objs


def deduplicate_and_exclude_none(data_list: Iterable) -> set:
    """
    deduplicate and exclude none by list
    :param data_list: data list
    :return:
    """
    data_set = set(data_list)
    data_set.discard(None)
    return data_set


def format_datetime_by_timestamp(timestamp: Union[int, str]) -> datetime.datetime:
    """
    :param timestamp:
    :return:
    """
    return datetime.datetime.fromtimestamp(int(timestamp), tz=pytz.utc)


def split_timestamp_to_date_times(
    timestamp: str,
) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    :param timestamp: timestamp-timestamp
    :return: date_time, date_time
    """
    if "-" not in timestamp:
        raise ValidationError(f"The '-' is not in split_timestamp!")
    start_timestamp, end_timestamp = timestamp.split("-", 1)
    if not start_timestamp.isdigit() or not end_timestamp.isdigit():
        raise ValidationError(
            f"start_timestamp:{start_timestamp} or end_timestamp:{end_timestamp} is not number!"
        )
    start_timestamp = int(start_timestamp)
    end_timestamp = int(end_timestamp)
    max_timestamp = datetime.datetime.max.timestamp()
    if start_timestamp > end_timestamp:
        raise ValidationError(
            f"start_timestamp:{start_timestamp} is greater than end_timestamp:{end_timestamp}!"
        )

    if start_timestamp > max_timestamp or end_timestamp > max_timestamp:
        raise ValidationError(
            f"The timestamp is not allowed to be greater than {max_timestamp}!"
        )
    start_datetime = format_datetime_by_timestamp(start_timestamp)
    end_datetime = format_datetime_by_timestamp(end_timestamp) + datetime.timedelta(
        milliseconds=999
    )
    return start_datetime, end_datetime


def gen_filename_with_date(
    filename_without_extension, extension, date_format="%Y%m%d%H%M%S"
):
    now = datetime.datetime.now()
    date_str = now.strftime(date_format)
    return f"{filename_without_extension}-{date_str}.{extension}"


def object_id_to_json(id):
    return {"$oid": str(id)}


def provide_unique_name(name, name_list):
    """
    :param name: is a string with the name you want to be unique
    :param name_list: is a list of  strings
    :return: return a a string that is not in list, ex:name(1)
    """
    old_name = name
    counter = 1
    while name in name_list:
        name = create_unique_name_counter(old_name, counter)
        counter += 1
    return name


def create_unique_name_counter(name, number):
    """
    :param name: string
    :param number: number
    :return: return name + number, ex: name(1)
    """
    return f"{name}({number})"


def get_current_month_start_and_end_date_time(
    month: Optional[int] = None, year: Optional[int] = None
) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    :param year:
    :param month:
    :return:
    """
    today = datetime.datetime.today()
    year = today.year if year is None else year
    month = today.month if month is None else month
    if month > 12:
        raise ValidationError(f"invalid month of {month}")
    start_date_time = parser.parse(f"{year}-{month}-01")
    next_month_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    end_date_time = parser.parse(f"{next_month_year}-{next_month}-01")
    return start_date_time, end_date_time


def get_month_date(date_time: datetime.datetime, language=None):
    language = language or get_language()
    return format_datetime(date_time, "MMMM yyyy", tzinfo=pytz.utc, locale=language)


def get_date_message_by_language(date_time: datetime.datetime, language):
    if not date_time:
        return
    return format_datetime(date_time, tzinfo=pytz.utc, locale=language)


def get_date_by_format(date, format_string):
    if format_string in DATE_FMT.values():
        return datetime.datetime.strptime(date, format_string).date()
    else:
        raise ValueError(f"date format not defined (current :{format_string})")


def datetime_to_text(date, language, format_string=None):
    """
        :param date: string representation of date in format en
        :param language: the language of robot
        :param format_string: True translate month to English or French
        :return: string representation of the date in current locale
        """
    try:
        if date:
            _date = get_date_by_format(date, DATE_FORMAT_EN)
            if not format_string:
                format_string = "{}"
            format_dict = json.loads(format_string)
            month_abbreviation = format_dict.get("month_abbreviation", True)
            if month_abbreviation:
                return " ".join(
                    [
                        "%02d" % _date.day,
                        MONTH_LANG_ABBREVIATION.get(language).get(_date.month),
                        str(_date.year),
                    ]
                )
            else:
                return _date.strftime(DATE_FORMAT_DICT.get(format_dict.get("format")))
    except:
        return date


def get_strftime_by_language(
    date_time: datetime.datetime, language: str, timezone_num: float = 1
) -> Optional[str]:
    """
        strftime_by_language
        :param date_time:
        :param language:
        :param timezone_num:
        :return:
        example:
        >>> strftime_by_language(datetime.utcnow(), 'en')
        >>> '03 July 2020 04:15:55 (GMT+1)'
        >>> strftime_by_language(datetime.utcnow(), 'fr')
        >>> '03 juillet 2020 04:16:00 (GMT+1)'
        """
    if not date_time:
        return
    gmt_date = date_time.astimezone(
        datetime.timezone(datetime.timedelta(hours=timezone_num))
    )
    create_time_str = datetime_to_text(
        gmt_date.strftime("%m/%d/%Y"), language, "{}"
    ) + gmt_date.strftime(" %H:%M:%S")
    return create_time_str + gmt_date.strftime(" (%Z)")


def profile(func):
    """Log time needed to run a method"""

    def wrap(*args, **kwargs):
        started_at = time()
        log_prefix = ""
        if args and isinstance(args[0], object):
            log_prefix = "%s." % args[0].__class__.__name__
        result = func(*args, **kwargs)
        logger.info(
            "Profiling method [%s%s]: %f s",
            log_prefix,
            func.__name__,
            time() - started_at,
        )
        return result

    return wrap


def replace_id_in_json(json_string, dictionary):
    if not json_string:
        return json_string
    string_list = re.split("([0-9a-f]{24,})", json_string)
    return "".join(dictionary.get(s, s) for s in string_list)


def get_customer_domain_url(
    init_url_pattern_name, customer_name=None, domain_code=None, kwargs=None
):
    # urlencode customer_name and domain_code, which may have special chars like `/`
    if customer_name:
        customer_name = quote(customer_name, safe="")
    if domain_code:
        domain_code = quote(domain_code, safe="")

    _kwargs = kwargs or {}
    action_type = _kwargs.pop("type", None)
    lang = _kwargs.pop("lang", None)
    if customer_name:
        if domain_code:
            kwargs = {"customer_name": customer_name, "domain_code": domain_code}
            kwargs.update(_kwargs)
            url = reverse(f"{init_url_pattern_name}_customer_domain", kwargs=kwargs)
        else:
            kwargs = {"customer_name": customer_name}
            kwargs.update(_kwargs)
            url = reverse(f"{init_url_pattern_name}_customer", kwargs=kwargs)
    else:
        url = reverse(init_url_pattern_name, kwargs=_kwargs)
    if action_type:
        url = url + f"?type={action_type}"
        if lang:
            url = url + f"&lang={lang}"
    else:
        if lang:
            url = url + f"?lang={lang}"
    return url


def get_initials_by_user(
    first_name: str, last_name: str, username: str, email: str
) -> str:
    if last_name and first_name:
        return last_name[0] + first_name[0]
    if last_name:
        return last_name[:2]
    if first_name:
        return first_name[:2]
    return username[:2] or email[:2]


def calculate_allow_bits(index: int, codes_length: int, max_bits=4):
    if index <= 0:
        allow_bits = 1
    else:
        allow_bits = int(math.log(index, codes_length)) + 1
        allow_bits = min(max_bits, allow_bits)
    return allow_bits


def index_to_code(index: int, cal_allow_bits=False) -> str:
    """
    parse index to domain code or robot code;
    this code is composed by from one to four character(s), possible characters are: a-z, A-Z, 0-9 and is generated
    incrementally;
    domain code is 2 fixed-length characters, and robot code is one to four character(s).
    :param index:
    :param cal_allow_bits:
    :return:
    """
    codes = string.digits + string.ascii_letters
    codes_length = len(codes)
    allow_bits = 2
    if cal_allow_bits:
        allow_bits = calculate_allow_bits(index, codes_length)

    assert 0 <= index < (codes_length ** allow_bits), "error index"
    code = ""
    for _ in range(allow_bits):
        i = index % codes_length
        index = int(index / codes_length)
        code = codes[i] + code
    return code


def get_user_full_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"


def format_user_name(user: Optional["GinerativUser"]) -> str:
    if not user:
        return _("l.deleted.user.placeholder")
    if user.first_name or user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.email


def get_percent(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0


def get_statistic_response_data(
    id_counts: dict, id_names: dict, total: int, deleted_name: Optional[str] = None
) -> dict:
    data_list = []
    deleted_name_count = 0
    for data_id, count in id_counts.items():
        name = id_names.get(data_id)
        if not name:
            deleted_name_count += count
            continue
        data_list.append(format_statistic_response_data(data_id, name, count, total))
    if deleted_name_count and deleted_name:
        data_list.append(
            format_statistic_response_data(
                deleted_name, deleted_name, deleted_name_count, total
            )
        )
    return {"data_list": data_list}


def format_statistic_response_data(
    data_id: str, name: str, count: int, total: int
) -> dict:
    data = {
        "id": data_id,
        "name": name,
        "count": count,
        "percent": get_percent(count, total),
    }
    return data


def get_bytes_hash_code(file_bytes: bytes) -> str:
    m = hashlib.md5()
    m.update(file_bytes)
    return m.hexdigest()


def get_the_range(total: int, part_of, total_part) -> tuple:
    """
    get the range from part_of
    :param total:
    :param part_of: part of total_part
    :param total_part:
    :return:
    """
    assert part_of >= 1, "'part_of' has to be greater than or equal to 1."
    assert total_part >= 1, "'total_part' has to be greater than or equal to 1."
    start = math.floor(total * ((part_of - 1) / total_part))
    end = math.floor(total * (part_of / total_part))
    return start, end


def get_search_text_q(query: QuerySet, text: str) -> Q:
    ids = query.search_text(f'"{text}"').values_list("id")
    q = Q(id__in=ids)
    return q


def get_percentage(part: int, whole: int, significant_digit: int = 0) -> str:
    if part > 0 and whole > 0:
        percent = 100 * float(part) / float(whole)
        significant_percent = round(percent, significant_digit)
        return f"{significant_percent:.{significant_digit}f}%"
    return "0"


def get_and_check_unaccented_string(accented_string: Optional[str]) -> Tuple[str, bool]:
    accented_string = accented_string or ""
    unaccented_string = unidecode(accented_string)
    return unaccented_string, accented_string == unaccented_string


def convert_string_to_lower_unaccented(accented_string: Optional[str]) -> str:
    accented_string = accented_string or ""
    lower_unaccented_string = unidecode(accented_string.lower())
    return lower_unaccented_string
