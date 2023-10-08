"""Module that contains a function to compare two dictionaries."""


def compare_responses(response1, response2):
    if response1 is None and response2 is None:
        return True
    if isinstance(response1, str) and isinstance(response2, str):
        return True
    if isinstance(response1, int) and isinstance(response2, int):
        return True
    if isinstance(response1, float) and isinstance(response2, float):
        return True
    if isinstance(response1, bool) and isinstance(response2, bool):
        return True
    if isinstance(response1, dict) and isinstance(response2, dict):
        return compare_dicts(response1, response2)
    if isinstance(response1, list) and isinstance(response2, list):
        return compare_list(response1, response2)
    if type(response1) != type(response2):
        return False
    return True


def compare_dicts(dict1, dict2):
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        error_message = "One of the arguments is not a dictionary."
        raise TypeError(error_message)

    if set(dict1.keys()) != set(dict2.keys()):
        return False

    for key in dict1:
        val1 = dict1[key]
        val2 = dict2[key]
        if not compare_responses(val1, val2):
            return False
    return True


def compare_list(list1, list2):
    if not isinstance(list1, list) or not isinstance(list2, list):
        error_message = "One of the arguments is not a list."
        raise TypeError(error_message)
    if len(list1) != len(list2):
        return False
    return all(compare_responses(elem1, elem2) for elem1, elem2 in zip(list1, list2, strict=True))
