import math
from datetime import datetime, timedelta

from pytz import UTC


def calculate_mbp(value: str, current_value: float, order, currencies: dict) -> float:
    from django_napse.core.models.wallets.currency import CurrencyPydantic

    ticker, price = value.split("|")
    price = float(price)

    current_amount = currencies.get(ticker, CurrencyPydantic(ticker=ticker, amount=0, mbp=0)).amount
    current_value = current_value if current_value is not None else 0
    received_quote = order.debited_amount - order.exit_amount_quote
    return (current_amount * current_value + received_quote) / (received_quote / price + current_amount)


def process_value_from_type(value, target_type, **kwargs) -> any:
    """Convert a value to a specific type."""
    target_type = target_type.lower()
    if value == "None":
        return None
    if target_type == "int":
        return int(value)
    if target_type == "float":
        return float(value)
    if target_type == "bool":
        match value:
            case "True" | "true":
                return True
            case "False" | "false":
                return False
            case _:
                return value
    elif target_type == "str":
        return str(value)
    elif target_type == "datetime":
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S%z").astimezone(UTC)
    elif target_type == "date":
        return datetime.strptime(value, "%Y-%m-%d").astimezone(UTC).date()
    elif target_type == "time":
        return datetime.strptime(value, "%H:%M:%S").astimezone(UTC).time()
    elif target_type == "timedelta":
        split = value.split(", ")
        days = split[0] if len(split) == 2 else "0 days"
        timestamp = split[1] if len(split) == 2 else split[0]
        days = int(days.split(" ")[0])
        t = datetime.strptime(timestamp, "%H:%M:%S").astimezone()
        return timedelta(days=days, hours=t.hour, minutes=t.minute, seconds=t.second)
    elif target_type == "None":
        return None
    elif target_type == "plugin_mbp":
        return calculate_mbp(
            value=value,
            current_value=kwargs["current_value"],
            order=kwargs["order"],
            currencies=kwargs["currencies"],
        )
    else:
        error_message = f"Unknown target_type: {target_type}"
        raise ValueError(error_message)


def round_up(number: float, decimals: int = 0) -> float:
    """Round a number up to a given number of decimals.

    Args:
    ----
    number (float): The number to round up.
    decimals (int, optional): The number of decimals to round up to. Defaults to 0.

    Returns:
    -------
    float: The rounded number.
    """
    multiplier = 10**decimals
    return math.ceil(number * multiplier) / multiplier


def round_down(number: float, decimals: int = 0) -> float:
    """Round a number down to a given number of decimals.

    Args:
    ----
    number (float): The number to round down.
    decimals (int, optional): The number of decimals to round down to. Defaults to 0.

    Returns:
    -------
    float: The rounded number.
    """
    multiplier = 10**decimals
    return math.floor(number * multiplier) / multiplier
