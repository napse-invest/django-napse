"""Module that contains a function to compare two dictionaries."""
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


def compare_responses(response1, response2, **kwargs):
    """Compare two responses.

    Kwargs:
    ------
    authorize_abstract_comparison (bool): Comparizon between an empty dict and a no empty dict is True. Same for list (default: False).
    """
    response1 = convert_response(response1)
    response2 = convert_response(response2)

    if response1 is None and response2 is None:
        return True
    if isinstance(response1, str) and isinstance(response2, str):
        return True
    if isinstance(response1, (int, float)) and isinstance(response2, (int, float)):
        return True
    if isinstance(response1, bool) and isinstance(response2, bool):
        return True
    if isinstance(response1, dict) and isinstance(response2, dict):
        return compare_dicts(response1, response2, **kwargs)
    if isinstance(response1, list) and isinstance(response2, list):
        return compare_list(response1, response2, **kwargs)
    if type(response1) != type(response2):
        error_msg: str = f"{type(response1)} != {type(response2)}"
        raise TypeError(error_msg)
    return True


def convert_response(response: ReturnList):
    if isinstance(response, ReturnList):
        return list(response)
    if isinstance(response, ReturnDict):
        return dict(response)
    return response


def compare_dicts(dict1, dict2, **kwargs):
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        error_message = "One of the arguments is not a dictionary."
        raise TypeError(error_message)

    # Only dict type comparaison
    if kwargs.get("authorize_abstract_comparison", False) and (dict1 == {} or dict2 == {}):
        return True

    if set(dict1.keys()) != set(dict2.keys()):
        error_msg: str = f"Dictionaries do not contain the same keys ({len(dict1.keys())} != {len(dict2.keys())})\n"
        error_msg += f"{dict1.keys()} != {dict2.keys()}"
        raise ValueError(error_msg)

    for key in dict1:
        val1 = dict1[key]
        val2 = dict2[key]
        try:
            compare_responses(val1, val2, **kwargs)
        except TypeError as error:
            error_msg = f"{error} on {key} key"
            raise TypeError(error_msg) from error
    return True


def compare_list(list1, list2, **kwargs):
    if not isinstance(list1, list) or not isinstance(list2, list):
        error_message = "One of the arguments is not a list."
        raise TypeError(error_message)

    # Only list type comparaison
    if kwargs.get("authorize_abstract_comparison", False) and (list1 == [] or list2 == []):
        return True

    if len(list1) != len(list2):
        error_msg: str = f"List haven't the same lenght ({len(list1)} != {len(list1)})"
        raise ValueError(error_msg)

    for i in range(len(list1)):
        try:
            compare_responses(list1[i], list2[i], **kwargs)
        except TypeError as error:
            error_msg = f"{error} on {i} index"
            raise TypeError(error_msg) from error
    return True
