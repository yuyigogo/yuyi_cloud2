# For constants defined
from enum import Enum
from functools import lru_cache


B = 1
KB = B * (2 ** 10)
MB = KB * (2 ** 10)

# max token expire days
MAX_EXPIRE_DAYS = 7
TOKEN_EXPIRE = 28800
# max file size
MAX_FILE_SIZE = 10 * MB

# model name's max length const
MAX_LENGTH_NAME = 200

DD_MM_YY = "%d/%m/%Y"
MM_DD_YY = "%m/%d/%Y"
YY_MM_DD = "%Y/%m/%d"
DD_MONTH_YY = "%d %m %Y"

EN_MONTH_ABBREVIATION = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

EN_MONTH_ABBREVIATION_REVERSE = {v: k for k, v in EN_MONTH_ABBREVIATION.items()}

FR_MONTH_ABBREVIATION = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}

FR_MONTH_ABBREVIATION_REVERSE = {v: k for k, v in FR_MONTH_ABBREVIATION.items()}

MONTH_LANG_ABBREVIATION = {"en": EN_MONTH_ABBREVIATION, "fr": FR_MONTH_ABBREVIATION}

MONTH_LANG_ABBREVIATION_REVERSE = {
    "en": EN_MONTH_ABBREVIATION_REVERSE,
    "fr": FR_MONTH_ABBREVIATION_REVERSE,
}

DATE_FORMAT_DICT = {
    "dd_mm_yy": DD_MM_YY,
    "mm_dd_yy": MM_DD_YY,
    "yy_mm_dd": YY_MM_DD,
    "month_abbreviation": DD_MONTH_YY,
}

MONTH_LANG_FORMAT = {"en": MM_DD_YY, "fr": DD_MM_YY}

"""set the date in database by language"""
DATE_FMT = {"fr": "%d/%m/%Y", "en": "%m/%d/%Y"}

DATE_FORMAT_EN = "%m/%d/%Y"  # format of date data in database

MAX_API_KEYS_NUM = 5

GOOGLE_DRIVER_ROOT_PATH_NAME = "gino"

FORMULA_DATE_FORMAT = "%m/%d/%Y"


class BaseEnum(Enum):
    @classmethod
    def is_valid(cls, value):
        """
        >>> class E(BaseEnum):
        ...     x = "a"
        ...     y = "b"

        >>> E.is_valid("a")
        True
        >>> E.is_valid("c")
        False
        >>> E.is_valid("x")
        False

        check is value is a valid value
        :param value:
        :return: True if valid else False
        """
        return value in cls._value2member_map_

    @classmethod
    @lru_cache
    def values(cls):
        """
        >>> class E(BaseEnum):
        ...     x = "a"
        ...     y = "b"

        >>> E.values()
        ['a', 'b']

        get all values of class
        :return: values list
        """
        return [x.value for x in cls]

    @classmethod
    def is_sup_list(cls, values: list) -> bool:
        """Report whether another list contains this list."""
        return set(values).issubset(set(cls.values()))

    @classmethod
    def to_dict(cls):
        return {x.name: x.value for x in cls}


class RoleLevel(str, BaseEnum):
    SUPER_ADMIN = 0
    ADMIN = 1
    NORMAL = 2

    @classmethod
    def allowed_role_level(cls):
        return [cls.ADMIN, cls.NORMAL]


ALL = "all"
