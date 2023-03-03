# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/3 17:37 
"""
from auto_macd_params import AutoMacdParams
from stock_tool import get_his_data, save_trade


def main(code, name, stock_type):
    his_data = get_his_data(code, stock_type)
    auto_result, trade_info = AutoMacdParams(code, name, his_data).main()
    save_trade(code, stock_type, auto_result, trade_info)


if __name__ == '__main__':
    pass