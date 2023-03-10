# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/9 11:03 
"""
from real_income import real_income
from stock_tool import get_his_data, save_trade
from auto_macd_params import AutoMacdParams
from sub_stocks_history import get_subs, get_sub, engine, text


def all_stocks_training():
    for code, name, stock_type in get_subs():
        df = get_his_data(code, stock_type)
        # amp = AutoMacdParams(code=code, name=name, stock_type=stock_type, data=df, n_calls=10)
        for trade_info, auto_result in AutoMacdParams.main(code=code, name=name, stock_type=stock_type, data=df, n_calls=10):
            save_result(code, stock_type, trade_info, auto_result)
            break


def training_one(code, stock_type):
    code, name, stock_type = get_sub(code=code, stock_type=stock_type)
    df = get_his_data(code, stock_type)
    # amp = AutoMacdParams(code=code, name=name, stock_type=stock_type, data=df, n_calls=10)
    for trade_info, auto_result in AutoMacdParams.main(
            code=code, name=name, stock_type=stock_type, data=df, n_calls=30, trad_days=130
    ):
        save_result(code, stock_type, trade_info, auto_result)


def save_result(code, stock_type, trade_info, auto_result):
    save_trade(code, stock_type, trade_info, auto_result)
    cols = ', '.join(f"`{str(i)}`" for i in auto_result.keys())
    values = ', '.join([f"'{str(i)}'" for i in auto_result.values()])
    insert_sql = f"REPLACE INTO auto_macd_result ({cols}) VALUES ({values})"
    with engine.connect() as conn:
        conn.execute(text(insert_sql))
        conn.commit()


if __name__ == '__main__':
    c = '002190'
    t = 1
    training_one(c, t)
    real_income(code=c, stock_type=t, start_dt='20220801')
