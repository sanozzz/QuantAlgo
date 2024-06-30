from execution_engine.execution_report import ExecutionReport
from custom_logging.logger import main_logger as logger

class OrderManager:
    def __init__(self, broker_api, strategy_config, alert_manager):
        self.broker_api = broker_api
        self.config = strategy_config
        self.execution_report = ExecutionReport()
        self.alert_manager = alert_manager
        self.active_orders = {}

    def place_order(self, symbol, side, quantity, price=None, stop_price=None):
        try:
            order_type = self.config['execution_settings'].get('order_type', 'market')
            limit_price = self.config['execution_settings'].get('limit_price', None)

            order = self.broker_api.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=limit_price if order_type == 'limit' else price,
                stop_price=stop_price
            )

            if order:
                self.active_orders[order['order_id']] = order
                self.execution_report.log_order(order)
                logger.info(f"Order placed successfully: {order}")
                self.alert_manager.send_alert(f"Order placed successfully: {order}", alert_type='slack')
                return order
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            self.alert_manager.send_alert(f"Failed to place order: {e}", alert_type='slack')
            return None

    def modify_order(self, order_id, quantity=None, price=None):
        try:
            order = self.broker_api.modify_order(order_id, quantity, price)
            self.active_orders[order_id] = order
            self.execution_report.log_order(order)
            logger.info(f"Order modified successfully: {order}")
            self.alert_manager.send_alert(f"Order modified successfully: {order}", alert_type='slack')
            return order
        except Exception as e:
            logger.error(f"Failed to modify order: {e}")
            self.alert_manager.send_alert(f"Failed to modify order: {e}", alert_type='slack')
            return None

    def cancel_order(self, order_id):
        try:
            order = self.broker_api.cancel_order(order_id)
            self.active_orders.pop(order_id, None)
            self.execution_report.log_order(order)
            logger.info(f"Order canceled successfully: {order}")
            self.alert_manager.send_alert(f"Order canceled successfully: {order}", alert_type='slack')
            return order
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            self.alert_manager.send_alert(f"Failed to cancel order: {e}", alert_type='slack')
            return None

    def get_order_status(self, order_id):
        try:
            order_status = self.broker_api.get_order_status(order_id)
            logger.info(f"Order status: {order_status}")
            self.alert_manager.send_alert(f"Order status: {order_status}", alert_type='slack')
            return order_status
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            self.alert_manager.send_alert(f"Failed to get order status: {e}", alert_type='slack')
            return None
