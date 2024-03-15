from datetime import timedelta

import environ
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from django_napse.core.models import Bot, Controller, DCABotConfig, DCAStrategy, SinglePairArchitecture
from django_napse.core.models.accounts.exchange import BinanceAccount
from django_napse.core.models.accounts.space import Space
from django_napse.core.models.fleets.fleet import Fleet
from django_napse.core.models.transactions.credit import Credit


class Command(BaseCommand):  # noqa
    help = "Create a prebuilt space with a fleet and a DCABot"

    def add_arguments(self, parser):  # noqa
        pass

    def handle(self, *args, **options):  # noqa
        env = environ.Env()
        with atomic():
            try:
                public_key = env.str("BINANCE_PUBLIC_KEY")
                private_key = env.str("BINANCE_PRIVATE_KEY")
            except ImproperlyConfigured:
                self.stdout.write(self.style.ERROR("Please set up BINANCE_PUBLIC_KEY and BINANCE_PRIVATE_KEY in .env file"))
            exchange_account = BinanceAccount.objects.get(
                public_key=public_key,
                private_key=private_key,
            )
            space = Space.objects.create(
                name="Prebuilt Space",
                description="We've created a space for you with all the necessary data to try out the app.",
                exchange_account=exchange_account,
            )
            Credit.objects.create(wallet=space.wallet, ticker="USDT", amount=100000)
            config = DCABotConfig.objects.create(space=space, settings={"timeframe": timedelta(minutes=1)})
            config5 = DCABotConfig.objects.create(space=space, settings={"timeframe": timedelta(minutes=5)})
            fleet = Fleet.objects.create(
                name="Prebuilt Fleet",
                exchange_account=exchange_account,
                clusters=[
                    {
                        "template_bot": Bot.objects.create(
                            name="Prebuilt DCABot",
                            strategy=DCAStrategy.objects.create(
                                config=config,
                                architecture=SinglePairArchitecture.objects.create(
                                    constants={
                                        "controller": Controller.get(
                                            exchange_account=exchange_account,
                                            base="BTC",
                                            quote="USDT",
                                            interval="1m",
                                        ),
                                    },
                                ),
                            ),
                        ),
                        "share": 0.3,
                        "breakpoint": 0,
                        "autoscale": False,
                    },
                    {
                        "template_bot": Bot.objects.create(
                            name="Prebuilt DCABot",
                            strategy=DCAStrategy.objects.create(
                                config=config,
                                architecture=SinglePairArchitecture.objects.create(
                                    constants={
                                        "controller": Controller.get(
                                            exchange_account=exchange_account,
                                            base="ETH",
                                            quote="USDT",
                                            interval="1m",
                                        ),
                                    },
                                ),
                            ),
                        ),
                        "share": 0.3,
                        "breakpoint": 0,
                        "autoscale": False,
                    },
                    {
                        "template_bot": Bot.objects.create(
                            name="Prebuilt DCABot",
                            strategy=DCAStrategy.objects.create(
                                config=config5,
                                architecture=SinglePairArchitecture.objects.create(
                                    constants={
                                        "controller": Controller.get(
                                            exchange_account=exchange_account,
                                            base="MATIC",
                                            quote="USDT",
                                            interval="1m",
                                        ),
                                    },
                                ),
                            ),
                        ),
                        "share": 0.2,
                        "breakpoint": 0,
                        "autoscale": False,
                    },
                    {
                        "template_bot": Bot.objects.create(
                            name="Prebuilt DCABot",
                            strategy=DCAStrategy.objects.create(
                                config=config5,
                                architecture=SinglePairArchitecture.objects.create(
                                    constants={
                                        "controller": Controller.get(
                                            exchange_account=exchange_account,
                                            base="MATIC",
                                            quote="USDT",
                                            interval="5m",
                                        ),
                                    },
                                ),
                            ),
                        ),
                        "share": 0.2,
                        "breakpoint": 0,
                        "autoscale": False,
                    },
                ],
            )
            fleet.invest(space=space, amount=10000, ticker="USDT")
            fleet.running = True
            fleet.save()
            self.stdout.write(self.style.SUCCESS("DCABot has been created successfully!"))
