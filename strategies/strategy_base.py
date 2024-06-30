# strategies/strategy_base.py

from abc import ABC, abstractmethod

class StrategyBase(ABC):
    def __init__(self, config):
        self.config = config
        self.data = None

    def set_data(self, data):
        self.data = data

    @abstractmethod
    def generate_signals(self):
        pass

    @abstractmethod
    def update_stop_loss(self, *args):
        pass

