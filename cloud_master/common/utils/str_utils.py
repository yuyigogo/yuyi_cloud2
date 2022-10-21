import random
import re
import string

from unidecode import unidecode


def to_ascii(string):
    """
    convert a utf-8 string to ascii string
    :param string: utf-8 string
    :return:  ascii string
    """
    return unidecode(string)


def remove_non_breaking_space(string):
    return string.replace(u"\xa0", u" ")


def gen_random_num_str(num: int = 8) -> str:
    r = random.sample(string.digits, num)
    random_str = "".join(r)
    return random_str


def generate_complex_password(
    length: int = 12,
    at_least_lower: int = 1,
    at_least_upper: int = 1,
    at_least_digit: int = 1,
    at_least_special_character: int = 1,
) -> string:
    customization_count = (
        at_least_lower + at_least_upper + at_least_digit + at_least_special_character
    )
    assert customization_count <= length
    #  Note that Spaces are also special characters
    special_characters = """ !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    digits = string.digits
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    samples = special_characters + digits + lowercase + uppercase
    random_chars = random.sample(lowercase, at_least_lower)
    random_chars += random.sample(uppercase, at_least_upper)
    random_chars += random.sample(digits, at_least_digit)
    random_chars += random.sample(special_characters, at_least_special_character)
    random_chars += random.sample(samples, length - customization_count)
    random.shuffle(random_chars)
    return "".join(random_chars)


def zfill_int_in_string(s: str, width: int = 10) -> str:
    return re.sub(r"\d+", lambda m: m.group(0).zfill(width), s)
