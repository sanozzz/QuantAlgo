import os
import json
from datetime import datetime
from custom_logging.logger import main_logger as logger

class ExecutionReport:
    def __init__(self, report_file='execution_report.json'):
        self.report_file = report_file
        self.executions = self.load_executions()

    def log_order(self, order):
        execution = {
            'order_id': order['order_id'],
            'symbol': order['symbol'],
            'side': order['side'],
            'quantity': order['quantity'],
            'price': order.get('price'),
            'stop_price': order.get('stop_price'),
            'order_type': order['order_type'],
            'status': order['status'],
            'timestamp': datetime.now().isoformat()
        }
        self.executions.append(execution)
        self.save_executions()
        logger.info(f"Order logged: {execution}")

    def load_executions(self):
        if os.path.exists(self.report_file):
            try:
                with open(self.report_file, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Failed to load executions: {e}")
                return []
        return []

    def save_executions(self):
        try:
            with open(self.report_file, 'w') as file:
                json.dump(self.executions, file, indent=4)
            logger.info("Executions saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save executions: {e}")

    def generate_report(self):
        # Placeholder for a more detailed report generation logic
        report = {
            'total_orders': len(self.executions),
            'executions': self.executions
        }
        logger.info(f"Generated execution report: {report}")
        return report

if __name__ == "__main__":
    # Example usage
    report = ExecutionReport()
    order = {
        'order_id': '12345',
        'symbol': 'NIFTY',
        'side': 'buy',
        'quantity': 10,
        'price': 15000,
        'order_type': 'market',
        'status': 'filled'
    }
    report.log_order(order)
    report.generate_report()
