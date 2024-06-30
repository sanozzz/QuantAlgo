import pandas as pd
import numpy as np


class PerformanceMetrics:
    def __init__(self, trades):
        self.trades = pd.DataFrame(trades)
        self.trades['net_profit'] = self.trades['exit_price'] - self.trades['entry_price']
        self.trades['return'] = self.trades['net_profit'] / self.trades['entry_price']

    def total_return(self):
        return self.trades['net_profit'].sum()

    def sharpe_ratio(self, risk_free_rate=0.0):
        mean_return = self.trades['return'].mean()
        std_return = self.trades['return'].std()
        sharpe_ratio = (mean_return - risk_free_rate) / std_return
        return sharpe_ratio

    def maximum_drawdown(self):
        cumulative_returns = (1 + self.trades['return']).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns / peak) - 1
        max_drawdown = drawdown.min()
        return max_drawdown

    def win_loss_ratio(self):
        wins = self.trades[self.trades['net_profit'] > 0].shape[0]
        losses = self.trades[self.trades['net_profit'] <= 0].shape[0]
        return wins / losses if losses != 0 else np.inf

    def average_gain(self):
        return self.trades[self.trades['net_profit'] > 0]['net_profit'].mean()

    def average_loss(self):
        return self.trades[self.trades['net_profit'] <= 0]['net_profit'].mean()

    def profit_factor(self):
        gross_profit = self.trades[self.trades['net_profit'] > 0]['net_profit'].sum()
        gross_loss = abs(self.trades[self.trades['net_profit'] <= 0]['net_profit'].sum())
        return gross_profit / gross_loss if gross_loss != 0 else np.inf

    def summary(self):
        return {
            'Total Return': self.total_return(),
            'Sharpe Ratio': self.sharpe_ratio(),
            'Maximum Drawdown': self.maximum_drawdown(),
            'Win/Loss Ratio': self.win_loss_ratio(),
            'Average Gain': self.average_gain(),
            'Average Loss': self.average_loss(),
            'Profit Factor': self.profit_factor()
        }
