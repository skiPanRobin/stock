# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/1 12:38
"""
import time
from datetime import datetime
import numpy as np
import pandas as pd
import talib
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

SPACE = [Real(0.3, 2, name='_fast'), Real(0.39, 3, name='_slow'), Integer(4, 40, name='signal')]


def _max_drawdown(cum_returns):
    # 计算最大回撤
    # 计算累计收益率
    # cum_returns = np.cumprod(1 + returns) - 1
    # 计算历史最高点
    cum_returns_max = np.maximum.accumulate(cum_returns)
    # 计算跌幅
    drawdown = (cum_returns_max - cum_returns) / (1 + cum_returns_max)
    # 计算最大回撤
    max_drawdown = np.max(drawdown)
    return max_drawdown


class AutoMacdParams:
    FAST = 12
    SLOW = 26
    SIGNAL = 9

    def __init__(self, code: str, name: str, data: pd.DataFrame, trad_days=130, n_calls=100):
        self._code = code
        self._name = name
        self._trad_days = trad_days
        self._data = data
        self._close = self._data['close']
        self.n_calls = n_calls
        self.space = [Real(0.3, 2, name='_fast'), Real(0.39, 3, name='_fast'), Integer(4, 40, name='signal')]

    def _objective(self):
        @use_named_args(dimensions=SPACE)
        def _objective_wrapper(_fast, _slow, signal):
            fast = round(_fast * self.FAST)
            slow = round(_slow * self.SLOW)
            if fast > slow:
                return 0
            cumulative_returns, returns, signals, max_drawdown = self.cur_cumulative_returns(fast, slow, signal)
            if float(max_drawdown) > 0.13:
                print(f'warning returns: {cumulative_returns.iloc[-1]}, drawdown: {max_drawdown} > 13per')
                return 0
            return -cumulative_returns.iloc[-1]

        return gp_minimize(_objective_wrapper, SPACE, n_calls=self.n_calls, random_state=0)

    def cur_cumulative_returns(self, fast: int, slow: int, signal: int):
        """
        计算累计回报
        """
        macd, signal_line, _ = talib.MACD(self._close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        # 计算收益率
        returns = np.diff(self._close) / self._close[:-1]
        # 计算交易信号
        signals = np.zeros_like(returns)
        signals[macd[1:] > signal_line[1:]] = 1  # 持仓
        signals[macd[1:] < signal_line[1:]] = 0  # 平仓
        # signals[macd[1:] < signal_line[1:]] = -1    # 做空
        # 只看最近TRAD_DAYS个交易日
        signals[:-min(self._trad_days, signals.shape[0])] = 0
        # 将交易信号向后移动一天
        signals = np.concatenate([[0], signals[:-1]])
        # 计算累积收益率
        strategy_returns = returns * signals
        cumulative_returns = np.cumprod(1 + strategy_returns) - 1
        # 计算回撤
        max_drawdown = _max_drawdown(cumulative_returns)
        print('最大回撤: ', max_drawdown, '收益: ', cumulative_returns.iloc[-1])
        return cumulative_returns, returns, signals, max_drawdown

    def _mark_trade_info(self, returns, signals, cumulative_returns):
        data = pd.DataFrame()
        data[['date']] = self._data[['date']]
        data[['close']] = self._data[['close']]
        data['returns'] = pd.concat([pd.Series([0]), returns], ignore_index=True)
        data['signals'] = pd.concat([pd.Series([0]), pd.Series(signals)], ignore_index=True)
        data['cumulative_returns'] = pd.concat([pd.Series([0]), pd.Series(cumulative_returns)], ignore_index=True)
        return data

    def _auto_result(self, fast, slow, signal, yields, trade_info, max_drawdown):
        signals = trade_info['signals']
        date = trade_info['date']
        hold_days = signals.sum()
        return {
            'date': time.strftime('%Y-%m-%d'),
            'code': self._code,
            's_dt': datetime.strftime(date.iloc[date.shape[0] - min(self._trad_days, date.shape[0])], '%Y-%m-%d'),
            'trade_days': self._trad_days,
            'name': self._name,
            'fast': fast,
            'slow': slow,
            'signal': int(signal),
            'hold_days': int(hold_days),
            'hold_status': '持有' if int(signals.iloc[-1]) == 1 else '空仓',
            'hold_rate': round(hold_days / self._trad_days, 4) * 100,
            'buy_times': (signals != signals.shift()).cumsum()[signals == 1].nunique(),
            'drawdown': round(max_drawdown, 4),
            'yields': yields,
        }

    def main(self):
        res = self._objective()
        fast = round(res.x[0] * self.FAST)
        slow = round(res.x[1] * self.SLOW)
        signal = res.x[2]
        yields = round(-res.fun, 4)
        print('最优参数 fast/slow/signal:', fast, slow, signal)
        print('最优目标函数值:', yields)
        cumulative_returns, returns, signals, max_drawdown = self.cur_cumulative_returns(fast, slow, signal)
        trade_info = self._mark_trade_info(returns, signals, cumulative_returns)
        auto_result = self._auto_result(fast, slow, signal, yields, trade_info, max_drawdown)
        return auto_result, trade_info


if __name__ == '__main__':
    pass
