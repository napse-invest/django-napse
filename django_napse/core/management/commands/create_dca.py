from datetime import timedelta

from django.core.management.base import BaseCommand

from django_napse.core.models import Bot, Controller, DCABotConfig, DCAStrategy, ExchangeAccount, SinglePairArchitecture, Space


class Command(BaseCommand):  # noqa
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):  # noqa
        pass

    def handle(self, *args, **options):  # noqa
        exchange_account = ExchangeAccount.objects.first()
        space = Space.objects.first()
        config = DCABotConfig.objects.create(space=space, settings={"timeframe": timedelta(minutes=1)})
        controller = Controller.get(
            exchange_account=exchange_account,
            base="ETH",
            quote="USDT",
            interval="1m",
        )
        architecture = SinglePairArchitecture.objects.create(constants={"controller": controller})
        strategy = DCAStrategy.objects.create(config=config, architecture=architecture)
        Bot.objects.create(name="Test Bot ETH/BTC", strategy=strategy)

        self.stdout.write(self.style.SUCCESS("DCABot has been created successfully!"))
