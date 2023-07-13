from django.apps import apps
from django.db import models


class BotSimManager(models.Manager):
    def create(self, bot_config, investment, start_date, end_date, simulation_reference=None, data=None):
        """Create a BotSim object and its associated BotSimDataPoint objects."""
        data = data or {}
        BotSimDataPoint = apps.get_model("_sims", "BotSimDataPoint")
        BotSimSetting = apps.get_model("_sims", "BotSimSetting")
        bot_sim = self.model(
            owner=bot_config.owner,
            bot_type=bot_config.bot_type,
            investment=investment,
            start_date=start_date,
            end_date=end_date,
            simulation_reference=simulation_reference,
        )
        bot_sim.save()
        for setting in bot_config.settings.all():
            BotSimSetting.objects.create(bot_sim=bot_sim, key=setting.key, value=setting.value, target_type=setting.target_type)

        must_have = ["prices", "values", "dates", "actions", "bases", "quotes"]
        for key in must_have:
            if key not in data:
                error_msg = f"Key {key} not in data"
                raise ValueError(error_msg)

        if "mbp" not in data.keys():
            data["mbp"] = [None for _ in data["prices"]]
        if "amounts" not in data.keys():
            data["amounts"] = [None for _ in data["prices"]]

        bot_sim.save()
        bulk_list = []
        for date, price, value, action, base, quote, mbp, amount in zip(
            data["dates"],
            data["prices"],
            data["values"],
            data["actions"],
            data["bases"],
            data["quotes"],
            data["mbp"],
            data["amounts"],
            strict=True,
        ):
            bulk_list.append(
                BotSimDataPoint(
                    bot_sim=bot_sim,
                    date=date,
                    price=price,
                    value=value,
                    action=action,
                    base=base,
                    quote=quote,
                    mbp=mbp,
                    amount=amount,
                ),
            )
            if len(bulk_list) == 1000 or date == data["dates"][-1]:
                BotSimDataPoint.objects.bulk_create(bulk_list)
                bulk_list = []
        return bot_sim
