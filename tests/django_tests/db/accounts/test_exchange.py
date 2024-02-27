import json
from typing import TYPE_CHECKING
from unittest import skipIf

from django_napse.core.models import BinanceAccount, Exchange, ExchangeAccount
from django_napse.core.settings import napse_settings
from django_napse.utils.errors import ExchangeAccountError
from django_napse.utils.model_test_case import ModelTestCase

if TYPE_CHECKING:
    from pathlib import Path

"""
python tests/test_app/manage.py test tests.django_tests.db.accounts.test_exchange -v2 --keepdb --parallel
"""


class ExchangeTestCase(ModelTestCase):
    model = Exchange
    skip_exchange_validation = True

    def simple_create(self):
        return self.model.objects.create(
            name="random exchange",
            description="random description",
        )

    def test_default_exchanges(self):
        base_configs = napse_settings.NAPSE_EXCHANGE_CONFIGS
        all_exchanges = Exchange.objects.all()

        self.assertEqual([exchange.name for exchange in all_exchanges], list(base_configs.keys()))

    def test_default_exchange_accounts(self):
        path: Path = napse_settings.NAPSE_SECRETS_FILE_PATH
        json_file = path.open("r")
        secrets = json.load(json_file)
        json_file.close()
        for exchange_id, exchange_secrets in secrets["Exchange Accounts"].items():
            exchange_name = exchange_secrets.pop("exchange")
            exchange = Exchange.objects.get(name=exchange_name)
            exchange_account = ExchangeAccount.objects.get(exchange=exchange, name=exchange_id)

            self.assertEqual(exchange_account.name, exchange_id)
            self.assertEqual(exchange_account.exchange.name, exchange_name)

            exchange_account_real_model = exchange_account.find()

            for key, value in exchange_secrets.items():
                self.assertEqual(getattr(exchange_account_real_model, key), value)


class BaseExchangeAccountTestCase(ModelTestCase):
    model = ExchangeAccount
    skip_exchange_validation = True

    def simple_create(self):
        exchange = Exchange.objects.create(
            name="random exchange",
            description="random description",
        )
        return self.model.objects.create(
            exchange=exchange,
            testing=True,
            name="random exchange account 1",
            description="random description",
        )


class ExchangeUtilsTestCase:
    @skipIf(napse_settings.NAPSE_IS_IN_PIPELINE, "No creadentials in pipelines")
    def test_ping(self):
        for exchange_account in self.model.objects.all():
            exchange_account.ping()

    def test_enough_accounts(self):
        self.assertTrue(self.model.objects.count() >= 1)

    def test_error_in_ping(self):
        with self.assertRaises(ExchangeAccountError.APIPermissionError):
            self.simple_create().ping()


class AccountUtilsBINANCETestCase(ExchangeUtilsTestCase, ModelTestCase):
    model = BinanceAccount
    exchange = "BINANCE"

    def simple_create(self):
        exchange = Exchange.objects.create(
            name="random exchange",
            description="random description",
        )
        return self.model.objects.create(
            exchange=exchange,
            testing=True,
            name="random exchange account 1",
            description="random description",
            private_key="random private key",
            public_key="random public key",
        )
