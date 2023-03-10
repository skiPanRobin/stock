# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/10 10:45 
"""
import numpy as np
import pandas as pd

from auto_macd_params import _max_drawdown
from sub_stocks_history import engine, text


def get_macd_res(code, stock_type, start_dt):
    with engine.connect() as conn:
        sql = f'SELECT `date`, `code`, `name`, `end_close`, hold_status FROM auto_macd_result ' \
              f'WHERE `date`>={start_dt} and `code`={code} and  stock_type={stock_type};'

        return pd.read_sql(text(sql), con=conn)


def income(data: pd.DataFrame):
    # 计算收益率
    _close = data['end_close']
    hold_status = data['hold_status']
    returns = np.diff(_close) / _close[:-1]
    # 收益信号
    hold_status.replace({'空仓': 0, "持有": 1}, inplace=True)
    # 计算累积收益率
    strategy_returns = returns * hold_status[:-1]
    cumulative_returns = np.cumprod(1 + strategy_returns) - 1
    # 计算回撤
    max_drawdown = _max_drawdown(cumulative_returns)
    print(f'code: {data[["code"]].iloc[0]}, name: {data[["name"]].iloc[0]}, 最大回撤: ', max_drawdown, '收益: ', cumulative_returns.iloc[-1])


def real_income(code, stock_type, start_dt):
    d = get_macd_res(code, stock_type, start_dt)
    income(d)


if __name__ == '__main__':
    real_income('000002', stock_type=1, start_dt='20220810')
