from enum import Enum, unique

# normal error msg code, for front-end developer to debug,
# and needn't to show for user;
# All error codes must be capitalized.


@unique
class StatusCode(Enum):
    """0----9999"""
    CUSTOMER_NAME_DUPLICATE = 1000
    SITE_NAME_DUPLICATE = 1001
    EXCEL_CONTAINS_MERGED_CELL = 1002
    IMPORT_EXCEL_IS_EMPTY = 1003
    EQUIPMENT_NAME_DUPLICATE = 1004

