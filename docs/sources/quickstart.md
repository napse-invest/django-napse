# Quickstart

!!! warning
    Nothing in this documentation constitutes investment advice. This documentation only explains and illustrates how to use the tool. Anything you do with the tool is under your sole responsibility, in accordance with the MIT license.

Once you've followed the [installation instructions](https://napse-invest.github.io/django-napse/#installation), let's take a look at how you can build your own bot.

## Exchange & Exchange Account
---

From the `secrets.json` file, the exchange **BINANCE** and the exchange account with the name **Binance EA_NAME** have been automatically built.

However, if you want to build another exchange or another exchange account, let's take a look at how to do it.

```python
from django_napse.core.models import Exchange, ExchangeAccount

# Create an exchange
exchange = Exchange.objects.create(
    name="BINANCE",
    description="...",
    )
exchange_account = ExchangeAccount.objects.create(
    exchange=exchange,
    testing=True, 
    name="ea name", 
    description="...", 
    )
```

## Space 
---

Let's build a space. A space is a place to categorize and manage your money.
```python
from django_napse.core.models import NapseSpace
space = NapseSpace.objects.create(
            name="Space",
            description="Space description",
            exchange_account=exchange_account,
        )
```

## Bot
---

Now let's build your first bot. A bot will trade on your behalf according to the strategy you have defined.
```python
from django_napse.core.models import Bot, EmptyBotConfig, Controller, SinglePairArchitecture, EmptyStrategy

# Create the config of the bot
config = EmptyBotConfig.objects.create(space=space, settings={"empty": True})
# The controller will discuss with the exchange's API
controller = Controller.get(
    exchange_account=exchange_account,
    base="BTC",
    quote="USDT",
    interval="1m",
)
# The architecture
        architecture = SinglePairArchitecture.objects.create(constants={"controller": controller})
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
```

## Fleet
---

Then it's time to build a fleet. A fleet is a set of bot. This allows bots to be scaled up according to the amount of money they manage.
```python
from django_napse.core.models import Fleet
Fleet.objects.create(
    name="Test Fleet",
    exchange_account=exchange_account,
    clusters=[
        {
            "template_bot": bot,
            "share": 0.7,
            "breakpoint": 1000,
            "autoscale": False,
        },
        {
            "template_bot": bot,
            "share": 0.3,
            "breakpoint": 1000,
            "autoscale": True,
        },
    ],
)

```