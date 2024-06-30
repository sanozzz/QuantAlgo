import requests
from execution_engine.base_broker_api import BaseBrokerAPI
from custom_logging.logger import main_logger as logger
import json
import os
import urllib.parse
class UpstoxAPI(BaseBrokerAPI):
    def __init__(self, api_key, api_secret, redirect_uri, token_file='token.json'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_uri = redirect_uri
        self.token_file = token_file
        self.access_token = self.load_access_token()

    def authenticate(self):
        # This should be replaced with the actual flow to get the auth_code
        auth_code = 'authorization_code_received_from_web'
        self.get_access_token(auth_code)

    def get_access_token(self, auth_code):
        url = 'https://api-v2.upstox.com/login/authorization/token'
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'redirect_uri': self.redirect_uri,
            'code': auth_code,
            'grant_type': 'authorization_code'
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            with open(self.token_file, 'w') as file:
                json.dump(data, file)
            return data.get('access_token')
        else:
            logger.error(f"Failed to obtain access token: {response.text}")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response headers: {response.headers}")
            logger.error(f"Response content: {response.content}")
            raise Exception(f"Failed to obtain access token: {response.text}")
    def load_access_token(self):
        if not os.path.exists(self.token_file):
            raise FileNotFoundError(f"Token file not found: {self.token_file}")

        with open(self.token_file, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                raise ValueError(f"Token file is not valid JSON: {self.token_file}")

        return data.get('access_token')


    def save_access_token(self, access_token):
        with open(self.token_file, 'w') as file:
            json.dump({'access_token': access_token}, file)

    def place_order(self, symbol, side, quantity, order_type='market', price=None, stop_price=None):
        url = "https://api.upstox.com/v2/order"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'order_type': order_type,
            'price': price,
            'stop_price': stop_price
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            order = response.json()
            return order
        else:
            logger.error(f"Failed to place order: {response.text}")
            return None

    def modify_order(self, order_id, quantity=None, price=None):
        url = f"https://api.upstox.com/v2/order/{order_id}/modify"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'quantity': quantity,
            'price': price
        }
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code == 200:
            order = response.json()
            return order
        else:
            logger.error(f"Failed to modify order: {response.text}")
            return None

    def cancel_order(self, order_id):
        url = f"https://api.upstox.com/v2/order/{order_id}/cancel"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            order = response.json()
            return order
        else:
            logger.error(f"Failed to cancel order: {response.text}")
            return None

    def get_order_status(self, order_id):
        url = f"https://api.upstox.com/v2/order/{order_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            order_status = response.json()
            return order_status
        else:
            logger.error(f"Failed to get order status: {response.text}")
            return None

    import requests
    import logging
    import urllib.parse

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    def get_current_price(self, symbol):
        try:
            # URL encode the symbol for the request
            encoded_symbol = urllib.parse.quote(symbol, safe='')
            url = f"https://api.upstox.com/v2/market-quote/ltp?instrument_key={encoded_symbol}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers)
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Text: {response.text}")
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Response JSON: {data}")
                if data['status'] == 'success':
                    # Replace '|' with ':' to match the response format
                    response_key = symbol.replace('|', ':')
                    logger.debug(f"Adjusted symbol for response: {response_key}")
                    if response_key in data['data']:
                        last_price = data['data'][response_key]['last_price']
                        return last_price
                    else:
                        logger.error(f"Symbol {response_key} not found in the response data")
                        return None
                else:
                    logger.error(f"API returned an error: {data}")
                    return None
            else:
                logger.error(f"Failed to get current price for {symbol}: {response.status_code} - {response.text}")
                return None
        except KeyError as ke:
            logger.error(f"Key error occurred while fetching the current price: {ke}")
            return None
        except Exception as e:
            logger.error(f"An error occurred while fetching the current price: {e}")
            return None

    def get_historical_data(self, symbol, interval, start_date, end_date):
        url = f"https://api.upstox.com/v2/historical/{symbol}?interval={interval}&start_date={start_date}&end_date={end_date}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            logger.error(f"Failed to get historical data for {symbol}: {response.text}")
            return None

    def get_intraday_data(self, symbol, interval, start_date, end_date):
        url = f"https://api.upstox.com/v2/intraday/{symbol}?interval={interval}&start_date={start_date}&end_date={end_date}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            logger.error(f"Failed to get intraday data for {symbol}: {response.text}")
            return None
