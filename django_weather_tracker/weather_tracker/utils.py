from datetime import datetime

import requests
from dateutil.parser import parse, ParserError


def call_function_on_str_fields_of_class(generic_class: any, string_function_lambda):
    for key, value in vars(generic_class).items():
        if value and isinstance(value, str):
            vars(generic_class)[key] = string_function_lambda(value)


def get_request(url: str) -> str or None:
    response = requests.get(url)
    return response.text if response else None


def parse_fuzzy_date_string(fuzzy_string: str) -> datetime or None:
    if len(fuzzy_string) > 50:
        print("Date Util Parser error: string too long, not bothering to parse")
        return None

    try:
        return parse(fuzzy_string, fuzzy_with_tokens=True)[0]
    except ParserError as e:
        print(f"Date Util Parser error {e}")
    except IndexError as e:
        print(f"dummy index erro as {e}")
    return None


def int_or_none(string: str) -> int or None:
    try:
        return int(string)
    except (ValueError, TypeError):
        return None
