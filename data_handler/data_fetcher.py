import pandas as pd
from custom_logging.logger import main_logger as logger

class DataFetcher:
    def __init__(self, broker_api):
        self.broker_api = broker_api

    def fetch_historical_data(self, symbol, interval, start_date, end_date):
        try:
            historical_data = self.broker_api.get_historical_data(symbol, interval, start_date, end_date)
            if not historical_data:
                logger.error("No historical data received.")
                return None
            data = pd.DataFrame(historical_data)
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None

    def fetch_intraday_data(self, symbol, interval):
        try:
            intraday_data = self.broker_api.get_intraday_data(symbol, interval)
            if not intraday_data:
                logger.error("No intraday data received.")
                return None
            data = pd.DataFrame(intraday_data)
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
            return data
        except Exception as e:
            logger.error(f"Error fetching intraday data: {e}")
            return None
