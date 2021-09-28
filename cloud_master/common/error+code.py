from enum import Enum, unique

# normal error msg code, for front-end developer to debug,
# and needn't to show for user;
# All error codes must be capitalized.


@unique
class StatusCode(Enum):
    """0----9999"""

    pass