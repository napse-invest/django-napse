import uuid
from datetime import datetime

from pytz import UTC

from django_napse.core.models import Bot, Controller, EmptyBotConfig, EmptyStrategy, SinglePairArchitecture
from django_napse.simulations.models import Simulation
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.db.simulations.test_simulation -v2 --keepdb --parallel
"""


class SimulationTestCase:
    model = Simulation

    def simple_create(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        architecture = SinglePairArchitecture.objects.create(
            constants={
                "controller": Controller.get(
                    exchange_account=self.exchange_account,
                    base="BTC",
                    quote="USDT",
                    interval="1m",
                ),
            },
        )
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        return Simulation.objects.create(
            space=self.space,
            bot=bot,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 1, 3, tzinfo=UTC),
            simulation_reference=uuid.uuid4(),
            data={},
        )

    def test_with_data(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        architecture = SinglePairArchitecture.objects.create(
            constants={
                "controller": Controller.get(
                    exchange_account=self.exchange_account,
                    base="BTC",
                    quote="USDT",
                    interval="1m",
                ),
            },
        )
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        simulation = Simulation.objects.create(
            space=self.space,
            bot=bot,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 1, 3, tzinfo=UTC),
            simulation_reference=uuid.uuid4(),
            data={
                "dates": [datetime.now(tz=UTC)],
                "values": [1],
                "actions": ["BUY"],
                "amounts": [1],
                "tickers": ["USDT"],
                "mbp": [10],
            },
        )
        simulation.info(verbose=False)

    def test_with_more_data(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        architecture = SinglePairArchitecture.objects.create(
            constants={
                "controller": Controller.get(
                    exchange_account=self.exchange_account,
                    base="BTC",
                    quote="USDT",
                    interval="1m",
                ),
            },
        )
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        simulation = Simulation.objects.create(
            space=self.space,
            bot=bot,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 1, 3, tzinfo=UTC),
            simulation_reference=uuid.uuid4(),
            data={
                "dates": [
                    datetime(2021, 1, 1, tzinfo=UTC),
                    datetime(2021, 1, 2, tzinfo=UTC),
                    datetime(2021, 1, 3, tzinfo=UTC),
                    datetime(2021, 1, 4, tzinfo=UTC),
                    datetime(2021, 1, 5, tzinfo=UTC),
                    datetime(2021, 1, 6, tzinfo=UTC),
                    datetime(2021, 1, 7, tzinfo=UTC),
                    datetime(2021, 1, 8, tzinfo=UTC),
                    datetime(2021, 1, 9, tzinfo=UTC),
                    datetime(2021, 1, 10, tzinfo=UTC),
                ],
                "values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "actions": ["BUY", "SELL", "SELL", "BUY", "KEEP", "KEEP", "BUY", "SELL", "BUY", "SELL"],
                "amounts": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "tickers": ["USDT", "USDT", "USDT", "USDT", "USDT", "USDT", "USDT", "USDT", "USDT", "USDT"],
                "mbp": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
            },
        )
        simulation.info(verbose=False)


class SimulationBINANCETestCase(SimulationTestCase, ModelTestCase):
    exchange = "BINANCE"
