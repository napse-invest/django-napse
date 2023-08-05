import hashlib
import uuid
from math import isclose
from time import sleep

from django.apps import apps
from django.db import models
from django.db.models import QuerySet

from django_napse.core.models.bots.bot_config import BotConfig
from django_napse.core.models.bots.controller import Controller
from django_napse.core.models.bots.managers import BotManager
from django_napse.core.models.connections import BotModification, Connection, SpecificArgsModification
from django_napse.core.models.orders import Order
from django_napse.core.models.transactions import Transaction
from django_napse.utils.constants import EXCHANGE_INTERVALS, EXCHANGE_PAIRS, EXCHANGE_TESTING, EXCHANGE_TICKERS, EXCHANGES
from django_napse.utils.errors import BotError, OrderError
from django_napse.utils.findable_class import FindableClass
from django_napse.utils.usefull_functions import process_value_from_type


class Bot(models.Model, FindableClass):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    name = models.CharField(max_length=100, default="Bot")
    pair = models.CharField(max_length=10, default="MATICUSDT")
    base = models.CharField(max_length=10, default="MATIC")
    quote = models.CharField(max_length=10, default="USDT")
    interval = models.CharField(max_length=10, default="1m")

    can_trade = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    specific_args = []
    to_hash_attributes = [
        "pair",
        "interval",
    ]

    # objects = BotManager()

    def __str__(self):
        return f"BOT {self.name=} ({self.pair=})"

    def info(self, verbose=True, beacon=""):  # pragma: no cover
        string = ""
        string += f"{beacon}Bot {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.__class__=}\n"
        string += f"{beacon}\t{self.base=}\n"
        string += f"{beacon}\t{self.quote=}\n"
        string += f"{beacon}\t{self.interval=}\n"
        string += f"{beacon}\t{self.testing=}\n"
        string += f"{beacon}\t{self.is_in_simulation=}\n"
        string += f"{beacon}\t{self.can_trade=}\n"

        for arg in self.specific_args:
            string += f"{beacon}\t{arg}={getattr(self, arg)}\n"

        # string += f"{beacon}Connections:\n"
        # if self.get_owners().count() == 0:
        #     string += f"{beacon}\tNone\n"
        # else:
        #     for connection in self.get_owners():
        #         conn_str = connection.info(verbose=False, beacon=beacon + "\t")
        #         string += f"{conn_str}\n"
        if verbose:
            print(string)
        return string

    @property
    def is_in_simulation(self):
        return hasattr(self, "simulation")

    @property
    def is_in_fleet(self):
        return hasattr(self, "bot_in_cluster")

    @property
    def testing(self):
        if self.is_in_simulation:
            return self.simulation.testing
        if self.is_in_fleet:
            return self.bot_in_cluster.cluster.fleet.testing
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def space(self):
        if self.is_in_simulation:
            return self.simulation.space
        if self.is_in_fleet:
            error_msg = "Bot is in a fleet and therefore doesn't have a space."
            raise BotError.NoSpace(error_msg)
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def exchange_account(self):
        if self.is_in_simulation:
            return self.simulation.space.exchange_account
        if self.is_in_fleet:
            return self.bot_in_cluster.cluster.fleet.exchange_account
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    def validate_settings(self):
        pass

    def validate_variables(self, **kwargs):
        pass

    @classmethod
    def hash_from_attributes(cls, **kwargs):
        """Classmethod to create a hash from the attributes of the bot.

        Returns
        -------
        int: The hash of the bot.
        """
        attr_dict = {}
        for attr_name in cls.to_hash_attributes:
            if attr_name not in kwargs:
                error_msg = f"Attribute {attr_name} is not in kwargs."
                raise BotError.InvalidSetting(error_msg)
        for attr_name, attr_value in kwargs.items():
            if attr_name in cls.to_hash_attributes:
                attr_dict[attr_name] = attr_value
        hash_values = [
            int(hashlib.sha256((str(attr_name) + str(attr_value)).encode("utf-8")).hexdigest(), 16) for attr_name, attr_value in attr_dict.items()
        ]
        return sum(hash_values)

    def __hash__(self) -> int:
        self = self.find()
        return self.hash_from_attributes(**{attr: getattr(self, attr) for attr in self.to_hash_attributes})

    def to_hash(self):
        """Calculate the hex value of the bot hash."""
        return hex(self.__hash__())

    def to_config(self, user) -> BotConfig:
        """Generate a BotConfig object from the bot, and associate it with a user.

        Args:
        ----
        user (User): The user to associate the BotConfig object with.

        Returns:
        -------
            BotConfig: The BotConfig object.
        """
        self = self.find()
        try:
            config = BotConfig.objects.get(
                space=self.space,
                bot_hash=self.to_hash,
            )
        except BotConfig.DoesNotExist:
            settings = {key: getattr(self, key) for key in self.customisable_attributes(self.exchange)}
            config = BotConfig.objects.create(
                space=self.space,
                bot_type=self.__class__.__name__,
                **settings,
            )
        return config

    @classmethod
    def customisable_attributes(cls, exchange) -> dict:
        """Classmethod to get the customisable attributes of the bot. (Used by the frontend).

        Args:
        ----
        exchange (Exchange): In order to know the accepted values for certain attributes,
        we need to know the exchange that will host the bot.

        Returns:
        -------
        dict : dict of the following shape:
        ```json
        {
            "name": {
                "target_type": "str",
                "type": "input_text",
                "max_length": 100,
                "value": "Bot",
                "plugins": [
                    {"type": "title", "value": "Name"},
                    {"type": "description", "value": "What shall we call this bot?"},
                ],
            },
            ...
        }
        ```
        """
        return {
            "name": {
                "target_type": "str",
                "type": "input_text",
                "max_length": 100,
                "value": "Bot",
                "plugins": [
                    {"type": "title", "value": "Name"},
                    {"type": "description", "value": "What shall we call this bot?"},
                ],
            },
            "pair": {
                "target_type": "str",
                "type": "search_choice",
                "choices": list(EXCHANGE_PAIRS[exchange.name].keys()),
                "value": "MATICUSDT",
                "plugins": [
                    {"type": "title", "value": "Pair"},
                    {"type": "description", "value": "The pair to trade on."},
                ],
            },
            "interval": {
                "target_type": "str",
                "type": "search_choice",
                "choices": list(EXCHANGE_INTERVALS[exchange.name]),
                "value": "1h",
                "plugins": [
                    {"type": "title", "value": "Interval"},
                    {"type": "description", "value": "The interval in between tardes."},
                ],
            },
        }
