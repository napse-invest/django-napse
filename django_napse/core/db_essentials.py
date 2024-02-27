import json

from django.apps import apps
from django.db.models.signals import post_migrate
from django.db.transaction import atomic
from django.dispatch import receiver

from django_napse.core.settings import napse_settings as settings


@receiver(post_migrate)
def create_exchanges(sender, **kwargs):
    Exchange = apps.get_model("django_napse_core", "Exchange")
    exchange_configs = settings.NAPSE_EXCHANGE_CONFIGS
    created_exchanges = []
    with atomic():
        for exchange_name, exchange_config in exchange_configs.items():
            _, created = Exchange.objects.get_or_create(name=exchange_name, description=exchange_config["description"])
            if created:
                created_exchanges.append(exchange_name)
    if len(created_exchanges) > 0:
        print(f"Created exchanges: {', '.join(created_exchanges)}")


@receiver(post_migrate)
def create_accounts(sender, **kwargs):
    Exchange = apps.get_model("django_napse_core", "Exchange")
    from django_napse.core.models.accounts.exchange import EXCHANGE_ACCOUNT_DICT

    try:
        with open(settings.NAPSE_SECRETS_FILE_PATH, "r") as json_file:
            secrets = json.load(json_file)
    except FileNotFoundError:
        with open(settings.NAPSE_SECRETS_FILE_PATH, "w") as json_file:
            json.dump({"Exchange Accounts": {}}, json_file)
        secrets = {"Exchange Accounts": {}}
    created_exchange_accounts = []

    with atomic():
        for exchange_id, exchange_secrets in secrets["Exchange Accounts"].items():
            exchange_name = exchange_secrets.pop("exchange")
            exchange = Exchange.objects.get(name=exchange_name)

            try:
                EXCHANGE_ACCOUNT_DICT[exchange_name].objects.get(
                    name=exchange_id,
                    exchange=exchange,
                    **exchange_secrets,
                )
            except EXCHANGE_ACCOUNT_DICT[exchange_name].DoesNotExist:
                EXCHANGE_ACCOUNT_DICT[exchange_name].objects.create(
                    name=exchange_id,
                    exchange=exchange,
                    default=True,
                    **exchange_secrets,
                )
                created_exchange_accounts.append(exchange_id)

    if len(created_exchange_accounts) > 0:
        print(f"Created exchange accounts: {', '.join(created_exchange_accounts)}")
