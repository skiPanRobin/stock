# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/9 11:03 
"""

from stock_tool import get_his_data, save_trade
from auto_macd_params import AutoMacdParams
from sub_stocks_history import get_subs, engine, text


class LiteMain:
    """
    精简版
    实现订阅跟踪, 推荐订阅买入, 跟踪买入收益
    """

    for code, name, stock_type in get_subs():
        df = get_his_data(code, stock_type)
        amp = AutoMacdParams(code=code, name=name, stock_type=stock_type, data=df, n_calls=10)
        trade_info, auto_result = amp.main()
        save_trade(code, stock_type, trade_info, auto_result)
        # if auto_result.get("hold_status") == '持仓':

        cols = ', '.join(f"`{str(i)}`" for i in auto_result.keys())
        values = ', '.join([f"'{str(i)}'" for i in auto_result.values()])
        insert_sql = f"INSERT INTO auto_macd_result ({cols}) VALUES ({values})"
        with engine.connect() as conn:
            conn.execute(text(insert_sql))
            conn.commit()

