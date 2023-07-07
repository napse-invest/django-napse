import json

from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_migrate
from django.db.transaction import atomic
from django.dispatch import receiver


@receiver(post_migrate)
def create_exchanges(sender, **kwargs):
    Exchange = apps.get_model("napse_core", "Exchange")
    exchange_configs = settings.NAPSE_EXCHANGE_CONFIGS
    created_exchanges = []
    for exchange_name, exchange_config in exchange_configs.items():
        _, created = Exchange.objects.get_or_create(name=exchange_name, description=exchange_config["description"])
        if created:
            created_exchanges.append(exchange_name)
    if len(created_exchanges) > 0:
        print(f"Created exchanges: {', '.join(created_exchanges)}")


@receiver(post_migrate)
def create_accounts(sender, **kwargs):
    from django_napse.napse_core.models.account.exchange import EXCHANGE_ACCOUNT_DICT

    Exchange = apps.get_model("napse_core", "Exchange")
    NapseAccount = apps.get_model("napse_core", "NapseAccount")
    with open(settings.NAPSE_SECRETS_FILE_PATH, "r") as json_file:
        secrets = json.load(json_file)
    created_accounts = []
    with atomic():
        for account in secrets["NapseAccounts"]:
            try:
                napse_account = NapseAccount.objects.get(napse_API_key=account["napse_API_key"])
            except NapseAccount.DoesNotExist:
                napse_account = NapseAccount.objects.create(
                    name=account["name"],
                    description=account["description"],
                    napse_API_key=account["napse_API_key"],
                )
                created_accounts.append(account["name"])
            exchange = Exchange.objects.get(name=account["exchange"])
            ExchangeAccount = EXCHANGE_ACCOUNT_DICT[exchange.name]
            ExchangeAccount.objects.get_or_create(
                exchange=exchange,
                napse_account=napse_account,
                **account["exchange_credentials"],
            )
    all_API_keys = []
    for napse_account in NapseAccount.objects.all():
        all_API_keys.append(napse_account.napse_API_key)
    all_secrets_API_keys = []
    for napse_account in secrets["NapseAccounts"]:
        all_secrets_API_keys.append(napse_account["napse_API_key"])
    for API_key in all_secrets_API_keys:
        if API_key not in all_API_keys:
            error_msg = f"API key {API_key} not found in NapseAccount objects"
            raise ValueError(error_msg)

    if len(created_accounts) > 0:
        print(f"Created Napse accounts: {', '.join(created_accounts)}")
