from enum import EnumMeta, StrEnum
from typing import Iterator


class CustomEnumMeta(EnumMeta):
    """Custom EnumMeta class to allow string comparison for Enums."""

    def __contains__(self, obj: object) -> bool:
        """Check if obj is a str in Enum's value or if it's an Enum in Enum's members."""
        if isinstance(obj, str):
            return any(obj == item for item in self)
        return super().__contains__(obj)

    def __iter__(self) -> Iterator:
        """Allow to iterate over the Enum's values."""
        return (self._member_map_[name].value for name in self._member_names_)

    def __str__(self) -> str:
        """Return the Enum's value."""
        return f"{[self._member_map_[name].value for name in self._member_names_]}"


class EXCHANGES(StrEnum, metaclass=CustomEnumMeta):
    """The exchange for a fleet or a bot."""

    BINANCE = "BINANCE"


class TRANSACTION_TYPES(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801, D101
    TRANSFER = "TRANSFER"
    CONNECTION_DEPOSIT = "CONNECTION_DEPOSIT"
    CONNECTION_WITHDRAW = "CONNECTION_WITHDRAW"
    ORDER_DEPOSIT = "ORDER_DEPOSIT"
    ORDER_PAYOUT = "ORDER_PAYOUT"
    ORDER_REFUND = "ORDER_REFUND"
    FLEET_REBALANCE = "FLEET_REBALANCE"


class ORDER_STATUS(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801, D101
    PENDING = "PENDING"
    READY = "READY"
    PASSED = "PASSED"
    ONLY_BUY_PASSED = "ONLY_BUY_PASSED"
    ONLY_SELL_PASSED = "ONLY_SELL_PASSED"
    FAILED = "FAILED"


class SIDES(StrEnum, metaclass=CustomEnumMeta):  # noqa: D101
    BUY = "BUY"
    SELL = "SELL"
    KEEP = "KEEP"


class DOWNLOAD_STATUS(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801, D101
    IDLE = "IDLE"
    DOWNLOADING = "DOWNLOADING"


class SIMULATION_STATUS(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801, D101
    IDLE = "IDLE"
    RUNNING = "RUNNING"


class MODIFICATION_STATUS(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801, D101
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"


class PLUGIN_CATEGORIES(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801
    """The category for a plugin."""

    PRE_ORDER = "PRE_ORDER"
    POST_ORDER = "POST_ORDER"


class PERMISSION_TYPES(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801
    """The permission type for a key."""

    ADMIN = "ADMIN"
    FULL_ACCESS = "FULL_ACCESS"
    READ_ONLY = "READ_ONLY"


class HISTORY_DATAPOINT_FIELDS(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801
    """The different fields for a history data point."""

    WALLET_VALUE = "WALLET_VALUE"
    AMOUNT = "AMOUNT"
    ASSET = "ASSET"
    PRICE = "PRICE"
    MBP = "MBP"
    LBO = "LBO"
    VALUE = "VALUE"


class HISTORY_DATAPOINT_FIELDS_WILDCARDS(StrEnum, metaclass=CustomEnumMeta):  # noqa: N801
    """The different fields for a history data point."""

    AMOUNT = "AMOUNT_"


for wildcard in HISTORY_DATAPOINT_FIELDS_WILDCARDS:
    duplicate = False
    for field in HISTORY_DATAPOINT_FIELDS:
        if field.startswith(wildcard):
            duplicate = True
            error_msg = f"Duplicate field {field} for wildcard {wildcard}"
            raise ValueError(error_msg)

ORDER_LEEWAY_PERCENTAGE = 10

DEFAULT_TAX = {
    "BINANCE": 0.1,
}

EXCHANGE_TICKERS = {
    "BINANCE": ["BTC", "ETH", "USDT", "BNB", "XRP", "ADA", "DOGE", "MATIC", "SOL", "DOT", "LTC", "TRX", "SHIB", "AVAX", "LINK", "ATOM", "UNI", "XLM"],
}
EXCHANGE_PAIRS = {
    "BINANCE": {ticker + "USDT": {"base": ticker, "quote": "USDT"} for ticker in EXCHANGE_TICKERS["BINANCE"] if ticker != "USDT"},
}
EXCHANGE_INTERVALS = {
    "BINANCE": ("1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"),
}
EXCHANGE_TESTING = {
    "BINANCE": [True],
}
EXCHANGE_SIMULATION = {
    "BINANCE": True,
}

STABLECOINS = {
    "BINANCE": ["USDT", "DAI", "BUSD"],
}

EXCHANGE_CONSTANTS = {
    "EXCHANGES": list(EXCHANGES),
    "EXCHANGE_TICKERS": EXCHANGE_TICKERS,
    "EXCHANGE_PAIRS": EXCHANGE_PAIRS,
    "EXCHANGE_INTERVALS": EXCHANGE_INTERVALS,
    "EXCHANGE_TESTING": EXCHANGE_TESTING,
    "EXCHANGE_SIMULATION": EXCHANGE_SIMULATION,
    "STABLECOINS": STABLECOINS,
}


MONTH_NUM_TO_STR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
