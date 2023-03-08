# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/6 11:49 
"""
import time
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import VARCHAR, INT, FLOAT, DECIMAL, CHAR, DATETIME
from urllib.parse import quote_plus

from mysql_tool import MysqlTool
from stock_tool import get_his_data

mt = MysqlTool()
uri = f'mysql+pymysql://{mt.user}:{quote_plus(mt.password)}@{mt.host}:{mt.port}/{mt.db}?charset={mt.charset}'
engine = create_engine(url=mt.uri)
# zh_name_table = 'stock_zh_ah_name'          # 存放所有A股最近交易截止日數據
# sub_stocks_history = 'sub_stocks_history'   # 存放A股訂閱股票所有每日交易數據


def stock_a(code):
    # print(code)
    # print(type(code))
    # 上证A股  # 深证A股
    if code.startswith('600') or code.startswith('6006') or code.startswith('601') or code.startswith(
            '000') or code.startswith('001') or code.startswith('002'):
        return True
    else:
        return False


def stock_a_filter_st(name):
    # print(code)
    # print(type(code))
    # 上证A股  # 深证A股
    if name.find("ST") == -1:
        return True
    else:
        return False


# 过滤价格，如果没有基本上是退市了。
def stock_a_filter_price(latest_price):
    # float 在 pandas 里面判断 空。
    if np.isnan(latest_price):
        return False
    else:
        return True


def get_code():
    code = time.strftime('%H%M')
    return f'bf1500pm' if code < '1500' else 'af1500pm'


def update_stock_zh_ah_name():
    data_row = get_his_data(code=get_code(), stock_type=5)

    data = pd.DataFrame()
    data[[
        'code', 'name', 'latest_price', 'quote_change', 'ups_downs', 'volume', 'turnover', 'amplitude', 'high',
        'low', 'open', 'closed', 'quantity_ratio', 'turnover_rate', 'pe_dynamic', 'pb'
    ]] = data_row[
        [
            '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高',
            '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率'
        ]]
    data['date'] = datetime_int = time.strftime("%Y%m%d")
    # with mt.cursor as cur:
    #     del_sql = " DELETE FROM `stock_zh_ah_name` where `date` = '%s' " % datetime_int
    #     cur.execute(del_sql)
    with engine.connect() as con:
        del_sql = " DELETE FROM `stock_zh_ah_name` where `date` = '%s' " % datetime_int
        con.execute(text(del_sql))
        con.commit()

    data.to_sql(
        name='stock_zh_ah_name', con=engine, index=False, if_exists='replace',
        dtype={
            'code': VARCHAR(10),
            'name': VARCHAR(20),
            'latest_price': FLOAT,
            'quote_change': FLOAT,
            'ups_downs': FLOAT,
            'volume': INT,
            'turnover': DECIMAL(40, 4),
            'amplitude': FLOAT,
            'high': FLOAT,
            'low': FLOAT,
            'open': FLOAT,
            'closed': FLOAT,
            'quantity_ratio': FLOAT,
            'turnover_rate': FLOAT,
            'pe_dynamic': FLOAT,
            'pb': FLOAT,
            'date': CHAR(8)
        }
    )


def upsert_fund_etf_daily_em():

    data_raw = get_his_data(code=get_code(), stock_type=6)
    data_raw.columns = [
        'code', 'name', 'type', 'today_nav', 'today_cum_nav', 'yesterday_nav',
        'yesterday_cum_nav', 'quote_change', 'ups_downs', 'latest_price',
        'discount_rate'
    ]
    data_raw.replace('---', '0')
    data_raw[['latest_time']] = time.strftime('%Y-%m-%d %H:%M:%S')
    data_raw[['date']] = time.strftime('%Y%m%d')
    data_raw.to_sql(
        name='fund_etf_daily_em', con=engine, index=False, if_exists='replace',
        dtype={
            'code': VARCHAR(10),
            'name': VARCHAR(40),
            'type': VARCHAR(10),
            'today_nav': FLOAT,
            'today_cum_nav': FLOAT,
            'yesterday_nav': FLOAT,
            'yesterday_cum_nav': FLOAT,
            'quote_change': FLOAT,
            'ups_downs': VARCHAR(20),
            'latest_price': VARCHAR(20),
            'discount_rate': VARCHAR(20),
            'latest_time': DATETIME,
            'date': CHAR(8)
        }

    )


if __name__ == '__main__':
    upsert_fund_etf_daily_em()
