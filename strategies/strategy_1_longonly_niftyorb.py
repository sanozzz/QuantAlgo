import datetime as dt
from custom_logging.logger import main_logger as logger


class Strategy1_LongOnly_NiftyORB:
    def __init__(self, config, position_manager):
        self.config = config
        self.position_manager = position_manager
        self.data = None

    def set_data(self, data):
        self.data = data

    def calculate_opening_range(self, historical_data):
        """
        Process first hour data
        1. Incase the time is above 10:15 am IST, it create two variables: opening_range_high, opening_range_low
        2. Incase the time is before 10:15 am, it returns none,none
        """

        current_time = dt.datetime.now().time()
        if current_time < dt.time(10, 15):
            logger.info("It is before 10:15 AM IST, so not processing first hour data yet.")
            return None, None

        if not historical_data.empty:
            try:
                # Extract first hour data
                first_hour_data = historical_data.between_time('09:15', '10:15')
                opening_range_high = first_hour_data['high'].max()
                opening_range_low = first_hour_data['low'].min()
                logger.info(
                    f"Successfully processed first hour data: opening_range_high = {opening_range_high}, opening_range_low = {opening_range_low}")
                return opening_range_high, opening_range_low
            except Exception as e:
                logger.error(f"Error processing first hour data: {e}")
                return None, None
        else:
            return None, None

    def generate_signals(self):
        opening_range_high, opening_range_low = self.calculate_opening_range(self.data)

        if opening_range_high is None or opening_range_low is None:
            logger.info("Opening range not yet determined; running other checks if any.")
            return None

        last_close_price = self.data.iloc[-1]['close']
        last_high_price = self.data.iloc[-1]['high']
        last_low_price = self.data.iloc[-1]['low']
        last_open_price = self.data.iloc[-1]['open']

        # Check conditions
        condition1 = last_close_price > opening_range_high
        condition2 = abs(last_high_price - last_close_price) <= self.config['wick_percentage'] * (
                    last_high_price - last_low_price)
        condition3 = last_close_price > last_open_price
        condition4 = last_close_price / opening_range_high <= self.config['close_price_above_opening_high_threshold']

        if condition1 and condition2 and condition3 and condition4:
            if not self.position_manager.has_open_position():
                logger.info("All conditions met: Generating buy signal")
                return {
                    'side': 'buy',
                    'stop_loss_price': last_low_price,
                    'quantity': self.config['quantity'],
                    'contract_symbol': self.config['contract_symbol']
                }
            else:
                logger.info("Position already open; not generating a new signal")
        else:
            logger.info(
                f"Not all conditions met: condition1 = {condition1}, condition2 = {condition2}, condition3 = {condition3}, condition4 = {condition4}")

        return None
