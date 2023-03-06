# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/2 10:45 
"""
import os
import time
import json

import pandas as pd
import akshare as ak

date = end_date = time.strftime('%Y%m%d')
START_DATE = '20180101'
ADJUST = "qfq"


def _single_api(code):
    d = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=START_DATE, adjust=ADJUST)
    d[['date']] = d[['日期']]
    d[['close']] = d[['收盘']]
    return d


def _industry_api(code):
    d = ak.stock_board_industry_hist_em(symbol=code, start_date=START_DATE, end_date=end_date, adjust=ADJUST)
    d[['date']] = d[['日期']]
    d[['close']] = d[['收盘']]
    return d


def _etf_api(code):
    d = ak.fund_etf_fund_info_em(fund=code, start_date=START_DATE, end_date=end_date)
    d[['date']] = d[['净值日期']]
    d[['close']] = d[['单位净值']]
    return d


def _index_api(code):
    return ak.stock_zh_index_daily(symbol=code)


def _zh_ah(code):
    print(f'codeless: {code}')
    return ak.stock_zh_a_spot_em()


_api_map = {
    1: _single_api,  # 个股
    2: _etf_api,  # 东财ETF
    3: _industry_api,  # 行业板块
    4: _index_api,  # 新浪指数
    5: _zh_ah
}


def _online_his_data(stock_type, code):
    return _api_map[stock_type](code)


def _save_trad_days(code, stock_type, data: pd.DataFrame):
    dir_name = _api_map[stock_type].__name__
    dir_path = f'./{dir_name}'
    file_name = f'{dir_path}/tb_{code}_{date}.zip.pickle'
    if os.path.exists(dir_path) is False:
        os.mkdir(path=dir_path)
    data.to_pickle(file_name, compression="gzip")


def _save_trad_status(code, stock_type, trad_status: dict):
    dir_name = _api_map[stock_type].__name__
    dir_path = f'./{dir_name}'
    file_name = f'{dir_path}/tbs_{code}_{date}.json'
    if os.path.exists(dir_path) is False:
        os.mkdir(path=dir_path)
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(obj=trad_status, fp=f, ensure_ascii=False, indent=4)


def save_trade(code, stock_type, data: pd.DataFrame, trad_status: dict):
    _save_trad_days(code, stock_type, data)
    _save_trad_status(code, stock_type, trad_status)


def get_his_data(code: str, stock_type: int):
    """
    获取 1.股票|2.ETF|3.行业|4.指数|5.當前A股數據
    :param code: A股股票代码|基金代码|行业板块中文|新浪指数
    :param stock_type: 1: 股票, 2: 基金ETF, 3: 行业板块, 4: 指数
    :return:
    """
    dir_name = _api_map[stock_type].__name__
    dir_path = f'./{dir_name}'
    file_name = f'{dir_path}/{code}_{date}.zip.pickle'
    if os.path.exists(file_name) is True:
        return pd.read_pickle(file_name, compression="gzip")
    else:
        if os.path.exists(dir_path) is False:
            os.mkdir(path=dir_path)
        his_data = _online_his_data(stock_type, code=code)
        his_data.to_pickle(file_name, compression="gzip")
        return his_data


def demo():
    c = '515400'
    st = 2
    data = get_his_data(c, stock_type=st)  # 东财etf 515400: 大数据ETF
    # get_his_data('515400', stock_type=3)
    print(data[['close']])


if __name__ == '__main__':
    demo()
