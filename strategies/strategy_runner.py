from position_management.position_manager import PositionManager
import threading
from datetime import datetime, time as dt_time, timedelta
from data_handler.data_fetcher import DataFetcher
from data_handler.data_processor import DataProcessor
import pandas_market_calendars as mcal
from custom_logging.logger import main_logger as logger  # Ensure logger is imported
import pytz

class StrategyRunner:
    def __init__(self, strategy_class, strategy_config, broker_api, alert_manager):
        self.strategy_class = strategy_class
        self.strategy_config = strategy_config
        self.broker_api = broker_api
        self.alert_manager = alert_manager
        self.position_manager = PositionManager(broker_api, None, strategy_config, alert_manager=alert_manager)
        self.strategy = strategy_class(strategy_config, self.position_manager)
        self.position_manager.set_strategy(self.strategy)
        self.start_time = dt_time.fromisoformat(strategy_config['start_time'])
        self.end_time = dt_time.fromisoformat(strategy_config['end_time'])
        self.interval = timedelta(minutes=strategy_config['interval'])
        self.market_calendar = mcal.get_calendar('XNSE')  # NSE market calendar
        self.next_run_time = self.get_next_run_time()

        self.data_fetcher = DataFetcher(broker_api)
        self.data_processor = DataProcessor()

    def get_next_run_time(self):
        timezone = pytz.timezone('Asia/Kolkata')
        today = datetime.now(timezone).date()
        next_run_time = timezone.localize(datetime.combine(today, self.start_time))
        while next_run_time <= datetime.now(timezone):
            next_run_time += self.interval
        return next_run_time

    def fetch_data(self):
        symbol = self.strategy_config['contract_symbol']
        interval = f"{self.strategy_config['candle_interval_minutes']}min"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        data = self.data_processor.fetch_and_merge_data(self.data_fetcher, symbol, interval, start_date, end_date)
        if data is None:
            logger.error("Data fetch failed, skipping strategy execution")
        return data

    def is_market_open(self, current_time):
        # Ensure current_time is in the Asia/Kolkata timezone
        if current_time.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False
        market_open = dt_time(9, 15)
        market_close = dt_time(15, 45)
        return market_open <= current_time.time() <= market_close

    def run(self):
        self.position_manager.start_monitoring()
        try:
            timezone = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(timezone)
            while self.is_market_open(current_time):
                if not self.is_market_open(current_time):
                    logger.info("Market is closed. Skipping strategy execution.")
                    time.sleep(60 * 60)  # Sleep for an hour before checking again
                    continue

                if dt_time(9, 15) <= current_time.time() <= dt_time(9, 30):
                    self.position_manager.reestablish_stop_losses()

                if current_time >= self.next_run_time:
                    data = self.fetch_data()
                    if data is not None:
                        self.strategy.set_data(data)
                        signal = self.strategy.generate_signals()
                        if signal:
                            self.position_manager.handle_signal(signal)
                            self.alert_manager.send_alert(f"Signal generated: {signal}", alert_type='slack')
                        else:
                            logger.info("No valid signal generated")
                    else:
                        logger.error("Data fetch failed, skipping strategy execution")

                    self.next_run_time += self.interval

                time.sleep(max(1, (self.next_run_time - current_time).total_seconds()))
        except KeyboardInterrupt:
            logger.info("Stopping position manager")
            self.position_manager.stop_monitoring()
