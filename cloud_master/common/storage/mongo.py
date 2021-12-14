def parse_illegal_key(key):
    """
    "." and "$" are invalid dictionary key in mongodb, replace with their unicode full width equivalents.
    :param key: illegal mongodb key
    :return: legal mongodb key
    """
    return key.replace("$", "\uff04").replace(".", "\uff0e")


MONGODB_MAX_VALUE = 2 ** 64


def transcend_mongodb_number_max(number: str) -> bool:
    try:
        number = int(number)
    except ValueError:
        number = float(number)
    return number > MONGODB_MAX_VALUE
