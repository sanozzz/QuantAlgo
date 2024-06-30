from abc import ABC, abstractmethod

class BaseBrokerAPI(ABC):
    @abstractmethod
    def place_order(self, symbol, side, quantity, order_type='market', price=None, stop_price=None):
        pass

    @abstractmethod
    def modify_order(self, order_id, quantity=None, price=None):
        pass

    @abstractmethod
    def cancel_order(self, order_id):
        pass

    @abstractmethod
    def get_order_status(self, order_id):
        pass

    @abstractmethod
    def get_current_price(self, symbol):
        pass

    @abstractmethod
    def get_historical_data(self, symbol, interval, start_date, end_date):
        pass

    @abstractmethod
    def get_intraday_data(self, symbol, interval, start_date, end_date):
        pass

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def get_access_token(self, auth_code):
        pass
