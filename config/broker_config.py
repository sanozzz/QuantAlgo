# config/broker_config.py

broker_config = {
    'default_broker': 'upstox',  # Default broker
    'brokers': {
        'upstox': {
            'class': 'UpstoxBrokerAPI',
            'module': 'execution_engine.upstox_broker_api',
        },
        # Add other brokers here
        # 'other_broker': {
        #     'class': 'OtherBrokerAPI',
        #     'module': 'execution_engine.other_broker_api',
        # },
    }
}
