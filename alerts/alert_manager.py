import requests
import json
from custom_logging.logger import main_logger as logger

class AlertManager:
    def __init__(self, config):
        self.slack_webhook_url = config.get('slack_webhook_url')
        if not self.slack_webhook_url:
            logger.error("Slack webhook URL not provided in configuration")

    def send_alert(self, message, alert_type='slack'):
        if alert_type == 'slack':
            self.send_slack_alert(message)
        else:
            logger.error(f"Unsupported alert type: {alert_type}")

    def send_slack_alert(self, message):
        if not self.slack_webhook_url:
            logger.error("Slack webhook URL not configured")
            return

        payload = {'text': message}
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.slack_webhook_url, data=json.dumps(payload), headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to send Slack alert: {response.text}")
            else:
                logger.info("Slack alert sent successfully")
        except Exception as e:
            logger.error(f"Exception while sending Slack alert: {e}")
