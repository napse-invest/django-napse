from typing import ClassVar

from django_napse.core.models import EmptyBotConfig, Space
from django_napse.utils.errors import BotConfigError
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.bots.test_bot_config -v2 --keepdb --parallel
"""


class BotConfigDefaultTestCase:
    def simple_create(self):
        return self.model.objects.create(space=self.space, settings=self.settings)

    def test_error_duplicate(self):
        self.simple_create()
        with self.assertRaises(BotConfigError.DuplicateBotConfig):
            self.simple_create()

    def test_missing_setting(self):
        with self.assertRaises(BotConfigError.MissingSettingError):
            self.model.objects.create(space=self.space, settings={})

    def test_duplicate_immutable(self):
        config = self.simple_create()
        config.duplicate_immutable()
        config.duplicate_immutable()

    def test_duplicate_other_space(self):
        config = self.simple_create()
        with self.assertRaises(ValueError):
            config.duplicate_other_space(self.space)
        new_space = Space.objects.create(name="Test Space 2", exchange_account=self.exchange_account, description="This is a test space")
        config.duplicate_other_space(new_space)


class EmptyBotConfigTestCase(BotConfigDefaultTestCase):
    model = EmptyBotConfig
    settings: ClassVar = {"empty": True}


class EmptyBotConfigBINANCETestCase(EmptyBotConfigTestCase, ModelTestCase):
    exchange = "BINANCE"
