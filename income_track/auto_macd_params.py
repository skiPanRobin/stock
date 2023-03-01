# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/1 12:38
"""
import time

import numpy as np
import pandas as pd
import talib
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

SPACE = [Real(0.3, 2, name='fast'), Real(0.39, 3, name='slow'), Integer(4, 40, name='signal')]


class AutoMacdParams:

    FAST = 12
    SLOW = 26
    SIGNAL = 9

    def __init__(self, code: str, name: str, data: pd.DataFrame, trad_days=130):
        self._code = code
        self._name = name
        self._trad_days = trad_days
        self._data = data

    @use_named_args(dimensions=SPACE)
    def _objective(self, _fast, _slow, signal):
        fast = round(_fast * self.FAST)
        slow = round(_slow * self.SLOW)
        close = self._data['close']
        macd, signal_line, _ = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        # 计算收益率
        returns = np.diff(close) / close[:-1]
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
        max_drawdown = self._max_drawdown(cumulative_returns)
        print('最大回撤: ', max_drawdown, '收益: ', cumulative_returns.iloc[-1])
        return -cumulative_returns.iloc[-1]

    def _max_drawdown(self, returns):
        # 计算累计收益率
        cum_returns = np.cumprod(1 + returns) - 1
        # 计算历史最高点
        cum_returns_max = np.maximum.accumulate(cum_returns)
        # 计算跌幅
        drawdown = (cum_returns_max - cum_returns) / (1 + cum_returns_max)
        # 计算最大回撤
        max_drawdown = np.max(drawdown)
        return max_drawdown

    def main(self):
        res = gp_minimize(self._objective, SPACE, n_calls=100, random_state=0)
        print('最优参数:', res.x)
        print('最优目标函数值:', -res.fun)
        print(f'fast:{int(res.x[0]*12)}, slow: {int(res.x[1]*26)}, signal: {res.x[2]}')
        return {
            'date': time.strftime('%Y-%m-%d'),
            'code': self._code,
            'name': self._name,
            'fast': round(res.x[0]*12),
            'slow': int(res.x[1]*26),
            'signal': res.x[2],
            'yields': -res.fun
        }


if __name__ == '__main__':
    pass