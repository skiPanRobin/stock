import numpy as np
import talib
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args
from skopt.plots import plot_convergence

from board_industry_am_trend import get_single_stock, Expma

api_data, _ = get_single_stock('000002')
data = Expma.fmt_api_date(api_data)
# 计算收益率
returns = np.diff(data['close']) / data['close'][:-1]
# 定义目标函数
@use_named_args(dimensions=[Integer(1, 20, name='fast'), Integer(2, 60, name='slow'), Integer(3, 15, name='signal')])
def objective(fast, slow, signal):
    # 读取数据
    # 这里需要根据具体的股票数据读取方式来实现
    # 计算MACD指标
    macd, signal_line, _ = talib.MACD(data['close'], fastperiod=fast, slowperiod=slow, signalperiod=signal)
    # 计算交易信号
    signals = np.zeros_like(returns)
    signals[macd[1:] > signal_line[1:]] = 1
    signals[macd[1:] < signal_line[1:]] = -1
    # 计算累积收益率
    strategy_returns = returns * signals
    cumulative_returns = np.cumprod(1 + strategy_returns) - 1
    # 返回负的累积收益率作为目标函数
    print(f'fast{fast}, slow: {slow}, signal:{signal}, 累计收益: {cumulative_returns.iloc[-1]}')
    return -cumulative_returns.iloc[-1]
    # return -1


# 定义参数空间
space = [Integer(5, 20, name='fast'), Integer(12, 60, name='slow'), Integer(2, 15, name='signal')]


# 进行优化
res = gp_minimize(objective, space, n_calls=10, random_state=0)

# 输出结果
print('最优参数:', res.x)
print('最优目标函数值:', -res.fun)

# 绘制收敛曲线
plot_convergence(res)


def test(fast, slow, signal):
    # 读取数据
    # 这里需要根据具体的股票数据读取方式来实现
    # 计算MACD指标
    macd, signal_line, _ = talib.MACD(data['close'], fastperiod=int(fast*12), slowperiod=int(slow*26), signalperiod=signal)
    # 计算收益率
    returns = np.diff(data['close']) / data['close'][:-1]
    # 计算交易信号
    signals = np.zeros_like(returns)
    signals[macd[1:] > signal_line[1:]] = 1
    signals[macd[1:] < signal_line[1:]] = -1
    # 计算累积收益率
    strategy_returns = returns * signals
    cumulative_returns = np.cumprod(1 + strategy_returns) - 1
    # 返回负的累积收益率作为目标函数
    return -cumulative_returns.iloc[-1]


print(test(res.x[0], res.x[1],res.x[2]))