import time

import numpy as np
import talib
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args
from skopt.plots import plot_convergence

from board_industry_am_trend import get_single_stock, Expma

space = [Real(0.3, 2, name='fast'), Real(0.39, 3, name='slow'), Integer(4, 40, name='signal')]
# space = [Integer(int(0.5*12), 2*12, name='fast'), Integer(int(0.5*26), 2*26, name='slow'), Integer(5, 60, name='signal')]
# TRAD_DAYS = 261  # 最近一年
TRAD_DAYS = 130  # 最近半年
code = '002466'


def get_data(code=code):
    data, _ = get_single_stock(code)
    return Expma.fmt_api_date(data)


# 定义目标函数
@use_named_args(dimensions=space)
def __objective(fast, slow, signal):
    """
    目标函数，根据给定的 MACD 参数计算出收益率并返回负的累计收益率作为目标值
    """
    if round(fast*12) > round(slow*26):
        return 1
    # 计算MACD指标
    data = get_data()
    macd, signal_line, _ = talib.MACD(data['close'], fastperiod=round(fast*12), slowperiod=round(slow*26), signalperiod=signal)
    # macd, signal_line, _ = talib.MACD(data['close'], fastperiod=fast, slowperiod=slow, signalperiod=signal)
    # 计算收益率
    returns = np.diff(data['close']) / data['close'][:-1]
    # 计算交易信号
    signals = np.zeros_like(returns)
    signals[macd[1:] > signal_line[1:]] = 1     # 持仓
    signals[macd[1:] < signal_line[1:]] = 0     # 平仓
    # signals[macd[1:] < signal_line[1:]] = -1    # 做空
    # 只看最近TRAD_DAYS个交易日
    signals[:-min(TRAD_DAYS, signals.shape[0])] = 0
    # 将交易信号向后移动一天
    signals = np.concatenate([[0], signals[:-1]])
    # 计算累积收益率
    strategy_returns = returns * signals
    cumulative_returns = np.cumprod(1 + strategy_returns) - 1
    # 计算回撤
    max_drawdown = _max_drawdown(cumulative_returns)
    print('最大回撤: ', max_drawdown, '收益: ', cumulative_returns.iloc[-1])
    return -cumulative_returns.iloc[-1]


def _max_drawdown(returns):
    # 计算累计收益率
    cum_returns = np.cumprod(1 + returns) - 1
    # 计算历史最高点
    cum_returns_max = np.maximum.accumulate(cum_returns)
    # 计算跌幅
    drawdown = (cum_returns_max - cum_returns) / (1 + cum_returns_max)
    # 计算最大回撤
    max_drawdown = np.max(drawdown)
    return max_drawdown


def _objective(fast, slow, signal, code):
    """
    目标函数，根据给定的 MACD 参数计算出收益率并返回负的累计收益率作为目标值
    """
    # 计算MACD指标
    data = get_data(code)
    macd, signal_line, _ = talib.MACD(data['close'], fastperiod=int(fast*12), slowperiod=int(slow*26), signalperiod=signal)
    # 计算收益率
    returns = np.diff(data['close']) / data['close'][:-1]
    # 计算交易信号
    signals = np.zeros_like(returns)
    signals[macd[1:] > signal_line[1:]] = 1     # 持仓
    signals[macd[1:] < signal_line[1:]] = 0     # 平仓
    # signals[macd[1:] < signal_line[1:]] = -1    # 做空
    # 只看最近TRAD_DAYS个交易日
    signals[:-min(TRAD_DAYS, signals.shape[0])] = 0
    # 将交易信号向后移动一天
    signals = np.concatenate([[0], signals[:-1]])
    # 计算累积收益率
    strategy_returns = returns * signals
    cumulative_returns = np.cumprod(1 + strategy_returns) - 1
    # 返回负的累积收益率作为目标函数
    print(f'fast:{int(fast*12)}, slow: {int(slow*26)}, signal: {signal}, 收益:{cumulative_returns.iloc[-1]}')
    # print(f'fast:{fast}, slow: {slow}, signal: {signal}')
    return -cumulative_returns.iloc[-1]


def main(obj):
    # 进行优化
    res = gp_minimize(obj, space, n_calls=100, random_state=0)
    # 输出结果
    print('最优参数:', res.x)
    print('最优目标函数值:', -res.fun)
    print(f'fast:{int(res.x[0]*12)}, slow: {int(res.x[1]*26)}, signal: {res.x[2]}')
    return int(res.x[0]*12), int(res.x[1]*26), res.x[2], -res.fun, {
        'date': time.strftime('%Y-%m-%d'),
        'code': ''
        'fast'
    }

    # print(f'fast:{int(res.x[0])}, slow: {int(res.x[1])}, signal: {res.x[2]}')
    # # 绘制收敛曲线
    # plot_convergence(res)



if __name__ == '__main__':
    main(__objective)
    _objective(1, 1, 9, code)
    # _objective(6/12, 13/26, 27, '000001')
    # print('最优参数:', res.x)
    # print('最优目标函数值:', -res.fun)
