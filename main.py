import time
import pandas as pd
import datetime as dt
from custom_logging.logger import main_logger as logger
from execution_engine.base_broker_api import BaseBrokerAPI
from config.config import config
from execution_engine.upstox_broker_api import UpstoxAPI
from strategies.strategy_runner import StrategyRunner
from alerts.alert_manager import AlertManager
import threading
from credentials import authenticate_and_get_token  # Import the function from credentials.py

from strategies.strategy_1_longonly_niftyorb import Strategy1_LongOnly_NiftyORB
def main():
    try:
        api_key, api_secret, redirect_uri, access_token = authenticate_and_get_token()
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return

    token_file = 'token.json'

    broker_api = UpstoxAPI(api_key, api_secret, redirect_uri, token_file=token_file)
    if not broker_api.access_token:
        logger.error("Access token is not available after authentication.")
        return

    alert_manager = AlertManager(config['alerts'])

    strategies = [
        (Strategy1_LongOnly_NiftyORB, config['strategy_1_longonly_niftyorb']),
        # Add other strategies here
    ]

    strategy_threads = []

    for strategy_class, strategy_config in strategies:
        runner = StrategyRunner(strategy_class, strategy_config, broker_api, alert_manager)
        thread = threading.Thread(target=runner.run)
        thread.start()
        strategy_threads.append(thread)

    for thread in strategy_threads:
        thread.join()

if __name__ == "__main__":
    main()
