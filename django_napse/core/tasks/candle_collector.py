import requests
from django.core.exceptions import ValidationError

from django_napse.core.models.bots.controller import Controller
from django_napse.core.tasks.base_task import BaseTask


class CandleCollectorTask(BaseTask):
    """Task to collect candles from binance's api and send it to controllers."""

    name = "candle_collector"
    interval_time = 30

    @staticmethod
    def build_candle(request_json: list[list[int], list[int]]) -> tuple[dict[str, int | float], dict[str, int | float]]:
        """Structure close_candle & current candle from the request.json().

        Candle shape: {"T": 1623000000000, "O": 1.0, "H": 1.0, "L": 1.0, "C": 1.0, "V": 1.0}.

        Args:
        ----
        request_json: response of binance's api

        Returns:
        -------
            closed_candle (dict[str, int | float]): last closed candle
            current_candle (dict[str, int | float]): current candle

        Raises:
        ------
            ValidationError: if request_json is not a list of 2 lists
        """
        dico_structure_label = ["T", "O", "H", "L", "C", "V"]

        # Check request
        if not isinstance(request_json, list):
            error_msg = f"request_json is not a list ({type(request_json)})"
            raise ValidationError(error_msg)

        if len(request_json) != 2:  # noqa
            error_msg = f"request_json must have 2 elements ({len(request_json)})"
            raise ValidationError(error_msg)

        if not isinstance(request_json[0], list) or not isinstance(request_json[1], list):
            error_msg = f"request_json is not a list of 2 lists ({type(request_json[0])}, {type(request_json[1])})"
            raise ValidationError(error_msg)

        if len(request_json[0]) != len(request_json[1]):
            error_msg = f"The 2 lists of requests json must have the same length ({len(request_json[0])}, {len(request_json[1])})"
            raise ValidationError(error_msg)

        if len(request_json[0]) < len(dico_structure_label) or len(request_json[1]) < len(dico_structure_label):
            error_msg = f"Request_json's lists are too short ({len(request_json[0])}, {len(request_json[1])})"
            raise ValidationError(error_msg)

        # Build candle with the good shape
        closed_candle: dict[str, int | float] = {}
        current_candle: dict[str, int | float] = {}
        for i, label in enumerate(dico_structure_label):
            if isinstance(request_json[0][i], int):
                closed_candle[label] = request_json[0][i]
                current_candle[label] = request_json[1][i]
            else:
                closed_candle[label] = float(request_json[0][i])
                current_candle[label] = float(request_json[1][i])
        return closed_candle, current_candle

    @staticmethod
    def request_get(pair: str, interval: str, api: str = "api") -> requests.Response:
        """Make a request to binance's api to get 2 candles (the last closed and the current one).

        Args:
        ----
        pair (str): pair of the candles
        interval (str): interval of the candles
        api (str, optional): api to use

        Returns:
        -------
            response of the request (requests.Response)
        """
        url = f"https://{api}.binance.com/api/v3/klines?symbol={pair}&interval={interval}&limit=2"
        try:
            req = requests.get(url, timeout=10)
        except requests.exceptions.ConnectionError:
            req = None
        return req

    def get_candles(self, pair: str, interval: str) -> tuple[dict[str, int | float], dict[str, int | float]]:
        """Get candles from binance's api.

        Retry automatically on all binance's backup api if the request failed.

        Args:
        ----
        pair: pair of the candles
        interval: interval of the candles

        Returns:
        -------
            closed_candle, current_candle

        Raises:
        ------
            ValidationError: if request failed on all apis
        """
        apis = ("api", "api1", "api2", "api3")

        for api in apis:
            request = self.request_get(pair, interval, api=api)
            # Valid request
            success_code = 200
            if request.status_code == success_code:
                return self.build_candle(request.json())
        # All requests failed
        error_msg = f"Impossible to get candles from binance's api (pair: {pair}, interval: {interval})"
        raise ValueError(error_msg)

    def run(self) -> None:
        """Run the task.

        Try to get the results of request of binance's api and send it to controller(s).
        If the request failed, the controller(s) is add to a list and controller(s) is this list try again (on all binance's backup api) at the end.
        """
        if not self.avoid_overlap(verbose=False):
            return
        self.info("Running CandleCollectorTask")

        failed_controllers: list["Controller"] = []
        failed_controllers_second_attempt: list["Controller"] = []
        all_orders = []
        for controller in Controller.objects.all():
            request = self.request_get(controller.pair, controller.interval, "api")
            success_code = 200
            if request is None or request.status_code != success_code:
                warning = f"Controller {controller.pk} failed on 'api'"
                self.warning(warning)
                failed_controllers.append(controller)
                continue
            closed_candle, current_candle = self.build_candle(request.json())
            all_orders += controller.send_candles_to_bots(closed_candle, current_candle)

        backup_apis = ("api1", "api2", "api3")
        for controller in failed_controllers:
            success = False
            for api in backup_apis:
                request = self.request_get(controller.pair, controller.interval, api)
                success_code = 200
                if request is not None and request.status_code == success_code:
                    closed_candle, current_candle = self.build_candle(request.json())
                    info = f"{controller} succeeded on '{api}'"
                    self.info(info)
                    success = True
                    break
            if success:
                all_orders += controller.send_candles_to_bots(closed_candle, current_candle)
            else:
                failed_controllers_second_attempt.append(controller)

        for controller in failed_controllers_second_attempt:
            error = f"{controller} failed on all apis"
            self.error(error)


CandleCollectorTask().delete_task()
CandleCollectorTask().register_task()
