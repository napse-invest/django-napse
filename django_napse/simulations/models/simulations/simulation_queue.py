import time
import uuid
from contextlib import suppress
from copy import deepcopy
from datetime import datetime, timedelta

from django.db import models

from django_napse.core.models.bots.bot import Bot
from django_napse.core.models.bots.controller import Controller
from django_napse.core.models.modifications import ArchitectureModification, ConnectionModification, StrategyModification
from django_napse.core.models.orders.order import Order, OrderBatch
from django_napse.core.models.transactions.credit import Credit
from django_napse.core.models.wallets.currency import CurrencyPydantic
from django_napse.simulations.models.datasets.dataset import Candle, DataSet
from django_napse.simulations.models.simulations.managers import SimulationQueueManager
from django_napse.utils.constants import EXCHANGE_INTERVALS, ORDER_LEEWAY_PERCENTAGE, ORDER_STATUS, SIDES, SIMULATION_STATUS
from django_napse.utils.errors import ControllerError

from .simulation import Simulation


class SimulationQueue(models.Model):
    """Queue wrapper for a simulation."""

    simulation_reference = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    space = models.ForeignKey("django_napse_core.Space", on_delete=models.CASCADE, null=True)
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

    def info(self, verbose: bool = True, beacon: str = "") -> str:  # noqa: FBT002, FBT001
        """Return info on SimulationQueue."""
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

    def setup_simulation(self) -> tuple[Bot, dict[str, any]]:
        """Setup investment and connections for the simulation."""
        self.space.simulation_wallet.find().reset()
        for investment in self.investments.all():
            Credit.objects.create(
                wallet=self.space.simulation_wallet,
                ticker=investment.ticker,
                amount=investment.amount,
            )
        new_bot = self.bot.copy()
        connection = new_bot.connect_to_wallet(self.space.simulation_wallet)
        for investment in self.investments.all():
            connection.deposit(investment.ticker, investment.amount)
        no_db_data = new_bot.architecture.prepare_db_data()
        return new_bot, no_db_data

    def cleanup_simulation(self, bot: Bot) -> None:
        """Reset the simulation: reset wallet & deactivate the bot."""
        self.space.simulation_wallet.reset()
        bot.hibernate()

    def preparation(self, bot, no_db_data):
        intervals = {controller.interval for controller in bot.controllers.values()}
        for interval in EXCHANGE_INTERVALS[next(iter(bot.controllers.values())).exchange_account.exchange.name]:
            if interval in intervals:
                min_interval = interval
                break

        currencies = next(iter(no_db_data["connection_data"].values()))["wallet"].currencies

        exchange_controllers = {controller: controller.exchange_controller for controller in bot.controllers.values()}

        data = {}
        datasets = []
        for controller in bot.controllers.values():
            datasets.append(DataSet.objects.create(controller=controller, start_date=self.start_date, end_date=self.end_date))
            with suppress(ControllerError.InvalidSetting):
                datasets.append(
                    DataSet.objects.create(
                        controller=Controller.get(
                            exchange_account=controller.exchange_account,
                            base=controller.base,
                            quote="USDT",
                            interval=min_interval,
                        ),
                        start_date=self.start_date,
                        end_date=self.end_date,
                    ),
                )
            with suppress(ControllerError.InvalidSetting):
                datasets.append(
                    DataSet.objects.create(
                        controller=Controller.get(
                            exchange_account=controller.exchange_account,
                            base=controller.quote,
                            quote="USDT",
                            interval=min_interval,
                        ),
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
        return data, currencies, exchange_controllers, min_interval

    def process_candle_data(self, candle_data, min_interval):
        processed_data = {"candles": {}, "extras": {}}
        current_prices = {}
        for controller, candle in candle_data.items():
            processed_data["candles"][controller] = {"current": candle, "latest": candle}
            if controller.quote == "USDT" and controller.interval == min_interval:
                price = candle["close"]
                current_prices[f"{controller.base}_price"] = price
        return processed_data, current_prices

    def append_data(
        self,
        connection_specific_args: dict,
        candle_data: dict,
        current_prices: dict,
        currencies: dict,
        currencies_before: dict,
        all_orders: list,
        date: datetime,
        dates: list,
        values: list,
        actions: list,
        prices: dict,
        total_amounts: dict,
        amounts: list,
        tickers: list,
        taxes: list,
        extras: dict,
    ):
        current_amounts = {}
        for controller in candle_data:
            current_amounts[f"{controller.base}_amount"] = currencies.get(
                controller.base,
                CurrencyPydantic(ticker=controller.base, amount=0, mbp=0),
            ).amount
            current_amounts[f"{controller.quote}_amount"] = currencies.get(
                controller.quote,
                CurrencyPydantic(ticker=controller.quote, amount=0, mbp=0),
            ).amount

        wallet_value = 0
        for ticker, currency in currencies.items():
            amount = currency.amount
            price = 1 if ticker == "USDT" else current_prices[f"{ticker}_price"]
            wallet_value += amount * price

        wallet_value_before = 0
        for ticker, currency in currencies_before.items():
            amount = currency.amount
            price = 1 if ticker == "USDT" else current_prices[f"{ticker}_price"]
            wallet_value_before += amount * price

        for index, order in enumerate(all_orders):
            dates.append(date + index * timedelta(seconds=1))
            values.append(round(wallet_value, 5))
            actions.append(order.side)
            for ticker_price in current_prices:
                prices[ticker_price] = [*prices.get(ticker_price, []), 1 if ticker_price == "USDT" else round(current_prices[ticker_price], 5)]
            for ticker_amount in current_amounts:
                total_amounts[ticker_amount] = [*total_amounts.get(ticker_amount, []), round(current_amounts[ticker_amount], 5)]
            taxes.append(round(order.fees * (current_prices[f"{order.fee_ticker}_price"] if order.fee_ticker != "USDT" else 1), 5))
            amounts.append(round(order.asked_for_amount, 5))
            tickers.append(order.asked_for_ticker)
            for plugin in extras:
                extras[plugin] = [*extras[plugin], connection_specific_args[plugin].get_value()]

    def quick_simulation(self, bot, no_db_data, verbose=True):
        data, currencies, exchange_controllers, min_interval = self.preparation(bot, no_db_data)
        _time = time.time()
        tpi = []
        dates = []
        values = []
        actions = []
        prices = {}
        total_amounts = {}
        taxes = []
        amounts = []
        tickers = []
        extras = {csa.key: [] for csa in next(iter(no_db_data["connection_data"].values()))["connection_specific_args"].values()}
        for date, candle_data in data.items():
            currencies_before = deepcopy(currencies)
            processed_data, current_prices = self.process_candle_data(
                candle_data=candle_data,
                min_interval=min_interval,
            )
            orders = bot._get_orders(data=processed_data, no_db_data=no_db_data)
            batches = {}
            for order in orders:
                debited_amount = order["asked_for_amount"] * (1 + ORDER_LEEWAY_PERCENTAGE / 100)
                if debited_amount > 0:
                    currencies[order["asked_for_ticker"]].amount -= debited_amount
                order["debited_amount"] = debited_amount

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
                    order.apply_modifications__no_db(
                        batch=batch,
                        modifications=[modification for modification in all_modifications if modification.order == order],
                        strategy=no_db_data["strategy"],
                        architecture=no_db_data["architecture"],
                        currencies=currencies,
                    )

                    currencies[controller.base] = currencies.get(controller.base, CurrencyPydantic(ticker=controller.base, amount=0, mbp=0))
                    currencies[controller.quote] = currencies.get(controller.quote, CurrencyPydantic(ticker=controller.quote, amount=0, mbp=0))
                    currencies[controller.base].amount += order.exit_amount_base
                    currencies[controller.quote].amount += order.exit_amount_quote

                all_orders += orders

            self.append_data(
                connection_specific_args=next(iter(no_db_data["connection_data"].values()))["connection_specific_args"],
                candle_data=candle_data,
                current_prices=current_prices,
                currencies=currencies,
                currencies_before=currencies_before,
                all_orders=all_orders,
                date=date,
                dates=dates,
                values=values,
                actions=actions,
                prices=prices,
                total_amounts=total_amounts,
                taxes=taxes,
                amounts=amounts,
                tickers=tickers,
                extras=extras,
            )
            tpi.append(time.time() - _time)
            _time = time.time()

        if verbose:
            print(f"Simulation ended.\nAverage TPI: {sum(tpi) / len(tpi)}")

        return Simulation.objects.create(
            space=self.space,
            bot=bot,
            start_date=self.start_date,
            end_date=self.end_date,
            simulation_reference=self.simulation_reference,
            data={
                "dates": dates,
                "values": values,
                "actions": actions,
                "taxes": taxes,
                "amounts": amounts,
                "tickers": tickers,
                **prices,
                **total_amounts,
                **extras,
            },
        )

    def irl_simulation(self, bot, no_db_data, verbose=True):
        data, _, exchange_controllers, min_interval = self.preparation(bot, no_db_data)
        _time = time.time()
        tpi = []
        dates = []
        values = []
        actions = []
        prices = {}
        total_amounts = {}
        taxes = []
        amounts = []
        tickers = []
        extras = {csa.key: [] for csa in next(iter(no_db_data["connection_data"].values()))["connection_specific_args"].values()}
        currencies = bot.connections.all()[0].wallet.to_dict().currencies
        for date, candle_data in data.items():
            currencies_before = deepcopy(currencies)
            processed_data, current_prices = self.process_candle_data(
                candle_data=candle_data,
                min_interval=min_interval,
            )

            orders, batches = bot.get_orders(data=processed_data)

            all_orders = []
            for controller, batch in batches.items():
                orders = controller.process_orders(
                    no_db_data={
                        "buy_orders": [order for order in orders if order.side == SIDES.BUY],
                        "sell_orders": [order for order in orders if order.side == SIDES.SELL],
                        "keep_orders": [order for order in orders if order.side == SIDES.KEEP],
                        "batches": [batch],
                        "exchange_controller": exchange_controllers[controller],
                        "min_trade": controller.min_notional / processed_data["candles"][controller]["latest"]["close"],
                        "price": processed_data["candles"][controller]["latest"]["close"],
                    },
                    testing=True,
                )

                controller.apply_orders(orders)
                for order in orders:
                    order.apply_modifications()
                    order.process_payout()
                all_orders += orders

            currencies = bot.connections.all()[0].wallet.to_dict().currencies
            self.append_data(
                connection_specific_args=bot.connections.all()[0].to_dict()["connection_specific_args"],
                candle_data=candle_data,
                current_prices=current_prices,
                currencies_before=currencies_before,
                currencies=currencies,
                all_orders=all_orders,
                date=date,
                dates=dates,
                values=values,
                actions=actions,
                prices=prices,
                total_amounts=total_amounts,
                taxes=taxes,
                amounts=amounts,
                tickers=tickers,
                extras=extras,
            )
            tpi.append(time.time() - _time)
            _time = time.time()

        if verbose:
            print(f"Simulation ended.\nAverage TPI: {sum(tpi) / len(tpi)}")

        return Simulation.objects.create(
            space=self.space,
            bot=bot,
            start_date=self.start_date,
            end_date=self.end_date,
            simulation_reference=self.simulation_reference,
            data={
                "dates": dates,
                "values": values,
                "actions": actions,
                "taxes": taxes,
                "amounts": amounts,
                "tickers": tickers,
                **prices,
                **total_amounts,
                **extras,
            },
        )

    def run_quick_simulation(self, verbose=True):
        self.status = SIMULATION_STATUS.RUNNING
        self.save()
        bot, no_db_data = self.setup_simulation()

        simulation = self.quick_simulation(bot=bot, no_db_data=no_db_data, verbose=verbose)

        self.cleanup_simulation(bot)
        self.status = SIMULATION_STATUS.IDLE
        self.save()
        return simulation

    def run_irl_simulation(self, verbose=True):
        self.status = SIMULATION_STATUS.RUNNING
        self.save()
        bot, no_db_data = self.setup_simulation()

        simulation = self.irl_simulation(bot=bot, no_db_data=no_db_data, verbose=verbose)

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
