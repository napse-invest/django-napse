from django_napse.core.models import EmptyBotConfig, Exchange, ExchangeAccount, NapseSpace
from django_napse.utils.errors import BotConfigError
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_bot_config -v2 --keepdb --parallel
"""


class BotConfigDefaultTestCase:
    def setUp(self):
        self.exchange = Exchange.objects.create(
            name="random exchange",
            description="random description",
        )
        self.exchange_account = ExchangeAccount.objects.create(
            exchange=self.exchange,
            testing=True,
            name="random exchange account 1",
            description="random description",
        )
        self.space = NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def simple_create(self):
        return self.model.objects.create(space=self.space, **self.settings)

    def test_to_bot(self):
        config = self.simple_create()
        bot = config.to_bot()
        for key, value in self.settings.items():
            self.assertEqual(getattr(bot, key), value)

    def test_hash(self):
        config = self.simple_create()
        self.assertEqual(config.bot_hash, config.to_bot().to_hash())
        self.assertEqual(config.bot_hash, self.hash)

    def test_error_duplicate(self):
        self.simple_create()
        with self.assertRaises(BotConfigError.DuplicateBotConfig):
            self.simple_create()

    def test_missing_setting(self):
        with self.assertRaises(BotConfigError.MissingSettingError):
            self.model.objects.create(space=self.space)

    def test_duplicate_immutable(self):
        config = self.simple_create()
        config.duplicate_immutable()
        config.duplicate_immutable()

    def test_duplicate_other_space(self):
        config = self.simple_create()
        with self.assertRaises(ValueError):
            config.duplicate_other_space(self.space)
        new_space = NapseSpace.objects.create(name="Test Space 2", exchange_account=self.exchange_account, description="This is a test space")
        config.duplicate_other_space(new_space)


class EmptyBotConfigTestCase(BotConfigDefaultTestCase, ModelTestCase):
    model = EmptyBotConfig
    settings = {}
