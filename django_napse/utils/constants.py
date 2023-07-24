from enum import Enum, EnumMeta


class CustomEnumMeta(EnumMeta):
    """Custom EnumMeta class to allow string comparison for Enums."""

    def __contains__(cls, obj):
        """Check if obj is a str in Enum's value or if it's an Enum in Enum's members."""
        if isinstance(obj, str):
            return any(obj == item for item in cls)
        return super().__contains__(obj)

    def __iter__(cls):
        """Allow to iterate over the Enum's values."""
        return (cls._member_map_[name].value for name in cls._member_names_)

    def __str__(cls) -> str:
        """Return the Enum's value."""
        return f"{[cls._member_map_[name].value for name in cls._member_names_]}"


class OPERATORS(Enum, metaclass=CustomEnumMeta):
    """The operator for a fleet."""

    EQUILIBRIUM = "EQUILIBRIUM"
    SPECIFIC_SHARES = "SPECIFIC_SHARES"


class EXCHANGES(Enum, metaclass=CustomEnumMeta):
    """The exchange for a fleet or a bot."""

    BINANCE = "BINANCE"


class TRANSACTION_TYPES(Enum, metaclass=CustomEnumMeta):
    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRADE = "TRADE"
    FLEET_REBALANCE = "FLEET_REBALANCE"
    DUST = "DUST"


class ORDER_STATUS(Enum, metaclass=CustomEnumMeta):
    PENDING = "PENDING"
    READY = "READY"
    PASSED = "PASSED"
    FAILED = "FAILED"


DEFAULT_TAX = {"BINANCE": 0.1}


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
    "BINANCE": [False],
}
EXCHANGE_SIMULATION = {
    "BINANCE": [True, False],
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
