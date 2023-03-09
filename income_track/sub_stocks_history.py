# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/6 11:49 
"""
import time
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
# from sqlalchemy.types import VARCHAR, INT, FLOAT, DECIMAL, CHAR, DATETIME

from mysql_tool import MysqlTool
from stock_tool import get_his_data

mt = MysqlTool
uri = f'mysql+pymysql://{mt.user}:{quote_plus(mt.password)}@{mt.host}:{mt.port}/{mt.db}?charset={mt.charset}'
engine = create_engine(url=uri)
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


def update_stock_zh_a_spot_em():
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
    with engine.connect() as con:
        del_sql = " DELETE FROM `stock_zh_a_spot_em` where `date` = '%s' " % datetime_int
        con.execute(text(del_sql))
        con.commit()

    data.to_sql(
        name='stock_zh_a_spot_em', con=engine, index=False, if_exists='append'
    )


def upsert_fund_etf_daily_em():
    data_raw = get_his_data(code=get_code(), stock_type=6)
    datetime_int = time.strftime('%Y%m%d')
    with engine.connect() as con:
        del_sql = " DELETE FROM `fund_etf_daily_em` where `date` = '%s' " % datetime_int
        con.execute(text(del_sql))
        con.commit()
    data_raw.columns = [
        'code', 'name', 'type', 'today_nav', 'today_cum_nav', 'yesterday_nav',
        'yesterday_cum_nav', 'quote_change', 'ups_downs', 'latest_price',
        'discount_rate'
    ]
    data_raw = data_raw.replace('---', '-999')
    data_raw[['latest_time']] = time.strftime('%Y-%m-%d %H:%M:%S')
    data_raw[['date']] = datetime_int
    data_raw.to_sql(
        name='fund_etf_daily_em', con=engine, index=False, if_exists='append',
    )


def add_etf_sub(etf_codes: tuple, sub_type=2):
    """添加etf订阅"""

    with engine.connect() as conn:
        sql = f"""
            REPLACE INTO sub_stocks 
            SELECT code, name, {sub_type}, 0,  now() 
            FROM fund_etf_daily_em ee 
            where ee.date=DATE_FORMAT(CURRENT_DATE, 'yyyymmdd') AND ee.`code` in {etf_codes};
            """
        conn.execute(text(sql))
        conn.commit()


def add_stock_sub(stock_code, sub_type=1):
    with engine.connect() as conn:
        sql = f"""
            REPLACE INTO sub_stocks 
            SELECT code, name, {sub_type}, 0,  now() 
            FROM stock_zh_a_spot_em ee 
            WHERE ee.date=DATE_FORMAT(CURRENT_DATE, 'yyyymmdd') AND ee.`code` in {stock_code};
            """
        conn.execute(text(sql))
        conn.commit()


def etf_codes_v1():
    return (
        '512660', '516150', '515880', '159792', '515790', '516090', '516790',
        '560800', '159658', '515400', '159991', '159806', '159996', '515220',
        '159819', '159869', '159919', '516110', '159801', '153050', '512170',
        '516780', '515700', '513330', '515210', '159980', '588360', '588080',
        '161725', '588080', '159766', '510050', '512480'
    )


def stock_codes_v1():
    return (
        '000063', '000519', '000651', '000821', '000938', '000977', '002049',
        '002050', '002363', '002371', '002460', '002466', '002532', '002594',
        '002607', '002738', '002756', '600031', '600036', '600316', '600418',
        '600522', '601390', '601888', '603019', '603201', '605259', '000002',
        '000001', '601127', '002532', '002190'
    )


def get_subs(stock_codes=(1, 2)):
    with engine.connect() as conn:
        sql = 'SELECT code, name, stock_type FROM sub_stocks WHERE is_delete=0'
        cur = conn.execute(text(sql))
        subs = list(cur.fetchall())
    for sub in subs:
        if sub[2] in stock_codes:
            yield sub   # code, name, stock_type


if __name__ == '__main__':
    # 手动更新, 并添加订阅
    # update_stock_zh_a_spot_em()
    # upsert_fund_etf_daily_em()
    # add_etf_sub(etf_codes_v1())
    # add_stock_sub(stock_codes_v1())
    for code, name, stock_type in get_subs((2, )):
        print(code, name, stock_type)
