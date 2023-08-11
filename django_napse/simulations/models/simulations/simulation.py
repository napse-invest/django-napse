import time
import uuid
from contextlib import suppress
from datetime import timedelta

from django.db import models

from django_napse.core.models.bots.controller import Controller
from django_napse.core.models.modifications import ArchitectureModification, ConnectionModification, StrategyModification
from django_napse.core.models.orders.order import Order, OrderBatch
from django_napse.core.models.transactions.credit import Credit
from django_napse.simulations.models.datasets.dataset import Candle, DataSet
from django_napse.simulations.models.simulations.managers import SimulationDataPointManager, SimulationManager, SimulationQueueManager
from django_napse.utils.constants import ORDER_LEEWAY_PERCENTAGE, ORDER_STATUS, SIDES, SIMULATION_STATUS
from django_napse.utils.errors import ControllerError
from django_napse.utils.usefull_functions import process_value_from_type


class Simulation(models.Model):
    simulation_reference = models.UUIDField(unique=True, editable=False, null=True)
    space = models.ForeignKey("django_napse_core.NapseSpace", on_delete=models.CASCADE, null=True)
    bot = models.OneToOneField("django_napse_core.Bot", on_delete=models.CASCADE, null=True, related_name="simulation")

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SimulationManager()

    def __str__(self) -> str:
        return f"SIMULATION {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Simulation {self.pk}:\n"
        string += f"{beacon}\t{self.bot=}\n"
        string += f"{beacon}\t{self.space=}\n"

        string += f"{beacon}\t{self.start_date=}\n"
        string += f"{beacon}\t{self.end_date=}\n"
        string += f"{beacon}\t{self.created_at=}\n"

        string += f"{beacon}Data points:\n"
        data_points = self.data_points.all().order_by("date")

        if data_points.count() > 10:
            for data_point in data_points[:5]:
                string += f"{beacon}\t{data_point.to_str()}\n"
            string += f"{beacon}\t...\n"
            for data_point in data_points[data_points.count() - 5 :]:
                string += f"{beacon}\t{data_point.to_str()}\n"
            string += f"{beacon}\t({data_points.count()} data points)\n"

        elif data_points.count() > 0:
            for data_point in data_points:
                string += f"{beacon}\t{data_point.to_str()}\n"

        else:
            string += f"{beacon}\tNo data points\n"
        if verbose:
            print(string)
        return string


class SimulationDataPoint(models.Model):
    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE, related_name="data_points")
    date = models.DateTimeField()
    value = models.FloatField()
    action = models.CharField(max_length=10)

    objects = SimulationDataPointManager()

    def __str__(self):
        return f"SIMULATION DATA POINT {self.pk}"

    def to_dict(self):
        extra_info = self.extra_info.all()
        return {
            "date": self.date,
            "value": self.value,
            "action": self.action,
            **{info.key: info.get_value() for info in extra_info},
        }

    def to_str(self):
        string = ""
        for key, value in self.to_dict().items():
            string += f"{key}: {value}\t"
        return string


class SimulationDataPointExtraInfo(models.Model):
    data_point = models.ForeignKey("SimulationDataPoint", on_delete=models.CASCADE, related_name="extra_info")
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
    target_type = models.CharField(max_length=64)

    def __str__(self):
        return f"SIMULATION DATA POINT EXTRA INFO {self.pk}"

    def get_value(self):
        return process_value_from_type(value=self.value, target_type=self.target_type)


class SimulationQueue(models.Model):
    simulation_reference = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    space = models.ForeignKey("django_napse_core.NapseSpace", on_delete=models.CASCADE, null=True)
    bot = models.OneToOneField("django_napse_core.Bot", on_delete=models.CASCADE, null=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    canceled = models.BooleanField(default=False)

    status = models.CharField(max_length=12, default=SIMULATION_STATUS.IDLE)
    completion = models.FloatField(default=0.0)
    eta = models.DurationField(blank=True, null=True)

    error = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = SimulationQueueManager()

    def __str__(self) -> str:
        return f"BOT SIM QUEUE {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}SimulationQueue {self.pk}:\n"
        string += f"{beacon}\t{self.bot=}\n"
        string += f"{beacon}\t{self.space=}\n"

        string += f"{beacon}\t{self.start_date=}\n"
        string += f"{beacon}\t{self.end_date=}\n"
        string += f"{beacon}\t{self.created_at=}\n"

        string += f"{beacon}Investments:\n"
        investments = self.investments.all()
        if investments.count() > 0:
            for investment in investments:
                string += f"{beacon}\t{investment}\n"
        else:
            string += f"{beacon}\tNo investments\n"
        if verbose:
            print(string)
        return string

    def setup_simulation(self):
        self.space.simulation_wallet.find().reset()
        for investment in self.investments.all():
            Credit.objects.create(
                wallet=self.space.simulation_wallet,
                ticker=investment.ticker,
                amount=investment.amount,
            )
        new_bot = self.bot.copy()
        connection = new_bot.connect_to(self.space.simulation_wallet)
        for investment in self.investments.all():
            connection.deposit(investment.ticker, investment.amount)
        no_db_data = new_bot.architecture.prepare_db_data()
        return new_bot, no_db_data

    def cleanup_simulation(self, bot):
        self.space.simulation_wallet.reset()
        bot.hibernate()

    def quick_simulation(self, bot, no_db_data):
        currencies = next(iter(no_db_data["connection_data"].values()))["wallet"]["currencies"]

        exchange_controllers = {controller: controller.exchange_controller for controller in bot.controllers.values()}

        data = {}
        datasets = []
        for controller in bot.controllers.values():
            datasets.append(DataSet.objects.create(controller=controller, start_date=self.start_date, end_date=self.end_date))
            with suppress(ControllerError.InvalidSetting):
                datasets.append(
                    DataSet.objects.create(
                        controller=Controller.get(exchange_account=controller.exchange_account, base=controller.base, quote="USDT", interval="1m"),
                        start_date=self.start_date,
                        end_date=self.end_date,
                    ),
                )
            with suppress(ControllerError.InvalidSetting):
                datasets.append(
                    DataSet.objects.create(
                        controller=Controller.get(exchange_account=controller.exchange_account, base=controller.quote, quote="USDT", interval="1m"),
                        start_date=self.start_date,
                        end_date=self.end_date,
                    ),
                )
        datasets = set(datasets)
        candles = Candle.objects.filter(dataset__in=datasets).order_by("open_time")
        open_times = candles.values_list("open_time", flat=True).distinct()
        for open_time in open_times:
            data[open_time] = {}
            for controller in bot.controllers.values():
                data[open_time][controller] = None
        for candle in candles:
            candle_dict = candle.to_dict()
            controller = candle_dict.pop("controller")
            data[candle.open_time][controller] = candle_dict

        for controller in bot.controllers.values():
            last_candle = None
            for open_time in open_times:
                if data[open_time][controller] is None:
                    data[open_time][controller] = last_candle
                else:
                    last_candle = data[open_time][controller]

        _time = time.time()
        tpi = []
        dates = []
        values = []
        actions = []
        prices = {}
        amounts = {}
        for date, candle_data in data.items():
            processed_data = {"candles": {}, "extras": {}}
            current_prices = {}
            current_amounts = {}
            for controller, candle in candle_data.items():
                processed_data["candles"][controller] = {"current": candle, "latest": candle}
                if controller.quote == "USDT" and controller.interval == "1m":
                    price = candle["close"]
                    current_prices[f"{controller.base}_price"] = price
                    current_amounts[f"{controller.base}_amount"] = currencies.get(controller.base, {"amount": 0})["amount"]
                    current_amounts[f"{controller.quote}_amount"] = currencies.get(controller.quote, {"amount": 0})["amount"]

            orders = bot._get_orders(data=processed_data, no_db_data=no_db_data)
            batches = {}
            for order in orders:
                currencies[order["asked_for_ticker"]]["amount"] -= order["asked_for_amount"] * (1 + ORDER_LEEWAY_PERCENTAGE / 100)
                order["debited_amount"] = order["asked_for_amount"] * (1 + ORDER_LEEWAY_PERCENTAGE / 100)

                controller = order["controller"]
                batches[controller] = OrderBatch(controller=controller)

            for batch in batches.values():
                batch.status = ORDER_STATUS.READY

            all_orders = []
            for controller, batch in batches.items():
                all_modifications = []
                controller_orders = [order for order in orders if order["controller"] == controller]
                order_objects = []
                for order in controller_orders:
                    order.pop("controller")
                    strategy_modifications = order.pop("StrategyModifications")
                    connection_modifications = order.pop("ConnectionModifications")
                    architecture_modifications = order.pop("ArchitectureModifications")
                    order = Order(batch=batch, **order)
                    order_objects.append(order)
                    for modification in strategy_modifications:
                        all_modifications.append(StrategyModification(order=order, **modification))
                    for modification in connection_modifications:
                        all_modifications.append(ConnectionModification(order=order, **modification))
                    for modification in architecture_modifications:
                        all_modifications.append(ArchitectureModification(order=order, **modification))

                orders = controller.process_orders(
                    no_db_data={
                        "buy_orders": [order for order in order_objects if order.side == SIDES.BUY],
                        "sell_orders": [order for order in order_objects if order.side == SIDES.SELL],
                        "keep_orders": [order for order in order_objects if order.side == SIDES.KEEP],
                        "batches": [batch],
                        "exchange_controller": exchange_controllers[controller],
                        "min_trade": controller.min_notional / processed_data["candles"][controller]["latest"]["close"],
                        "price": processed_data["candles"][controller]["latest"]["close"],
                    },
                    testing=True,
                )
                for order in orders:
                    if order.side == SIDES.BUY and (batch.status == ORDER_STATUS.PASSED or batch.status == ORDER_STATUS.ONLY_BUY_PASSED):
                        for modification in [modification for modification in all_modifications if modification.order == order]:
                            modification._apply(
                                strategy=no_db_data["strategy"],
                                architecture=no_db_data["architecture"],
                            )
                    currencies[controller.base] = currencies.get(controller.base, {"amount": 0, "mbp": 0})
                    currencies[controller.quote] = currencies.get(controller.quote, {"amount": 0, "mbp": 0})
                    currencies[controller.base]["amount"] += order.exit_amount_base
                    currencies[controller.quote]["amount"] += order.exit_amount_quote

                all_orders += orders

            wallet_value = 0
            for ticker, currency in currencies.items():
                amount = currency["amount"]
                price = 1 if ticker == "USDT" else current_prices[f"{ticker}_price"]
                wallet_value += amount * price

            for index, order in enumerate(all_orders):
                dates.append(date + index * timedelta(seconds=1))
                values.append(round(wallet_value, 5))
                actions.append(order.side)
                for ticker_price in current_prices:
                    prices[ticker_price] = [*prices.get(ticker_price, []), 1 if ticker_price == "USDT" else round(current_prices[ticker_price], 5)]
                for ticker_amount in current_amounts:
                    amounts[ticker_amount] = [*amounts.get(ticker_amount, []), round(current_amounts[ticker_amount], 5)]

            tpi.append(time.time() - _time)
            _time = time.time()
        print(sum(tpi) / len(tpi))
        return Simulation.objects.create(
            space=self.space,
            bot=bot,
            start_date=self.start_date,
            end_date=self.end_date,
            simulation_reference=self.simulation_reference,
            data={"dates": dates, "values": values, "actions": actions, **prices, **amounts},
        )

    def run_quick_simulation(self):
        self.status = SIMULATION_STATUS.RUNNING
        self.save()
        bot, no_db_data = self.setup_simulation()

        simulation = self.quick_simulation(bot=self.bot, no_db_data=no_db_data)

        self.cleanup_simulation(bot)
        self.status = SIMULATION_STATUS.IDLE
        self.save()
        return simulation

    def is_finished(self):
        return self.status == SIMULATION_STATUS.IDLE and self.completion == 100

    def get_status(self):
        """Return a dictionary with the status of the BotSimQueue.

        Dict shape:
        ```json
        {
            "status": "RUNNING",
            "completion": 56.9,
            "eta": 00:01:04,
            "position_in_queue": 0,
            "error": false,
        }
        ```
        """
        return {
            "status": self.status,
            "completion": self.completion,
            "eta": self.eta,
            "position_in_queue": SimulationQueue.objects.filter(created_at__lt=self.created_at, error=False).count(),
            "error": self.error,
        }

    def cancel(self):
        """Stop the BotSim."""
        self.canceled = True
        self.save()
