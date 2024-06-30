config = {
    'strategy_1_longonly_niftyorb': {
        'wick_percentage': 0.1,
        'close_price_above_opening_high_threshold': 1.003,
        'quantity': 25,
        'contract_symbol': 'NSE_INDEX|Nifty 50',
        'execution_settings': {
            'order_type': 'market',  # can be 'market', 'limit', etc.
            'limit_price': None,     # specify limit price if order_type is 'limit'
        },
        'sleep_interval': 30,       # Interval for running the strategy in minutes
        'candle_interval_minutes': 30,  # Interval for the candles in minutes
        'start_time': '09:15',  # Start time of the strategy
        'end_time': '15:45',    # End time of the strategy
        'interval': 30,         # Strategy run interval in minutes
    },
    'alerts': {
        'slack_webhook_url': 'https://hooks.slack.com/services/your/slack/webhook/url'
    }
}
