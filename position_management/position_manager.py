import time
import threading
from custom_logging.logger import main_logger as logger
from execution_engine.order_manager import OrderManager

class PositionManager:
    def __init__(self, broker_api, strategy=None, strategy_config=None, check_interval=60, stop_loss_buffer=0.01, alert_manager=None):
        self.broker_api = broker_api
        self.order_manager = OrderManager(broker_api, strategy_config, alert_manager)
        self.strategy = strategy
        self.config = strategy_config
        self.check_interval = check_interval
        self.stop_loss_buffer = stop_loss_buffer
        self.current_price = None
        self.running = False
        self.thread = None
        self.position_open = False
        self.initial_stop_loss = None
        self.current_stop_loss = None
        self.alert_manager = alert_manager

    def set_strategy(self, strategy):
        self.strategy = strategy

    def handle_signal(self, signal):
        logger.info(f"[{self.strategy.__class__.__name__}] Handling signal: {signal}")
        if signal['side'] == 'buy':
            order = self.order_manager.place_order(
                symbol=signal['contract_symbol'],
                side='buy',
                quantity=signal['quantity']
            )
            if order:
                self.position_open = True
                self.initial_stop_loss = signal['stop_loss_price']
                self.current_stop_loss = signal['stop_loss_price'] - (signal['stop_loss_price'] * self.stop_loss_buffer)
                logger.info(f"[{self.strategy.__class__.__name__}] Position opened with stop loss: {self.initial_stop_loss} and current stop loss: {self.current_stop_loss}")
        elif signal['side'] == 'sell':
            order = self.order_manager.place_order(
                symbol=signal['contract_symbol'],
                side='sell',
                quantity=signal['quantity']
            )
            if order:
                self.position_open = False
                self.initial_stop_loss = None
                self.current_stop_loss = None
                logger.info(f"[{self.strategy.__class__.__name__}] Position closed")
                if self.alert_manager:
                    self.alert_manager.send_alert(f"Position closed: {signal}", alert_type='slack')

    def start_monitoring(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_stop_loss)
        self.thread.start()
        logger.info(f"[{self.strategy.__class__.__name__}] Started monitoring stop loss")

    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info(f"[{self.strategy.__class__.__name__}] Stopped monitoring stop loss")

    def _monitor_stop_loss(self):
        while self.running:
            self.update_current_price()
            if self.current_price and self.current_stop_loss:
                logger.info(f"[{self.strategy.__class__.__name__}] Current price: {self.current_price}, Current stop loss: {self.current_stop_loss}")
                if self.current_price <= self.current_stop_loss:
                    logger.info(f"[{self.strategy.__class__.__name__}] Stop loss hit: Generating sell signal")
                    sell_signal = {
                        'side': 'sell',
                        'quantity': self.strategy.config['quantity'],
                        'contract_symbol': self.strategy.config['contract_symbol']
                    }
                    order = self.order_manager.place_order(
                        symbol=sell_signal['contract_symbol'],
                        side=sell_signal['side'],
                        quantity=sell_signal['quantity']
                    )
                    if order:
                        self.position_open = False
                        self.initial_stop_loss = None
                        self.current_stop_loss = None
                        logger.info(f"[{self.strategy.__class__.__name__}] Position closed due to stop loss hit")
                        if self.alert_manager:
                            self.alert_manager.send_alert(f"Stop loss hit: Position closed for {sell_signal['contract_symbol']}", alert_type='slack')
            time.sleep(self.check_interval)

    def update_current_price(self):
        try:
            self.current_price = self.broker_api.get_current_price(self.strategy.config['contract_symbol'])
            logger.info(f"[{self.strategy.__class__.__name__}] Updated current price: {self.current_price}")
        except Exception as e:
            logger.error(f"[{self.strategy.__class__.__name__}] Failed to update current price: {e}")

    def update_stop_loss(self, last_high_price):
        self.strategy.update_stop_loss(last_high_price)
        self.current_stop_loss = self.strategy.current_stop_loss - (self.strategy.current_stop_loss * self.stop_loss_buffer)
        logger.info(f"[{self.strategy.__class__.__name__}] Updated stop loss in PositionManager: {self.current_stop_loss}")

    def has_open_position(self):
        return self.position_open

    def reestablish_stop_losses(self):
        if self.position_open:
            symbol = self.strategy.config['contract_symbol']
            stop_loss_price = self.current_stop_loss
            if stop_loss_price:
                order = self.broker_api.place_order(
                    symbol=symbol,
                    side='sell',
                    quantity=self.strategy.config['quantity'],
                    stop_price=stop_loss_price,
                    order_type='stop_loss'
                )
                if order:
                    logger.info(f"Re-established stop loss for {symbol} at {stop_loss_price}")
                    if self.alert_manager:
                        self.alert_manager.send_alert(f"Re-established stop loss for {symbol} at {stop_loss_price}",
                                                      alert_type='slack')
