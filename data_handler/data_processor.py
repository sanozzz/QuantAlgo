import pandas as pd
from custom_logging.logger import main_logger as logger

class DataProcessor:
    def clean_data(self, data):
        # Implement your data cleaning logic here
        return data

    def resample_data(self, data, interval):
        return data.resample(interval).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last'
        }).dropna()

    def calculate_indicators(self, data):
        # Implement your indicator calculation logic here
        return data

    def fetch_and_merge_data(self, data_fetcher, symbol, interval, start_date, end_date):
        historical_data = data_fetcher.fetch_historical_data(symbol, interval, start_date, end_date)
        intraday_data = data_fetcher.fetch_intraday_data(symbol, interval)

        if historical_data is not None and intraday_data is not None:
            merged_data = pd.concat([historical_data, intraday_data])
            merged_data = merged_data[~merged_data.index.duplicated(keep='last')]
            return merged_data
        elif historical_data is not None:
            return historical_data
        elif intraday_data is not None:
            return intraday_data
        else:
            return None
