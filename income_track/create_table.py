# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/7 18:39 
"""

from sqlalchemy import create_engine, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, FLOAT, DECIMAL, CHAR, BOOLEAN

from mysql_tool import MysqlTool as mt

engine = create_engine(url=mt.uri)
Base = declarative_base()


class StockZhASpotEm(Base):
    """
    东方财富网-沪深京 A 股-实时行情
    当15点之后更新的数据,latest_price作为当日收盘价
    """
    __tablename__ = 'stock_zh_a_spot_em'
    __table_args__ = (
        PrimaryKeyConstraint('date', 'code'),
        {'comment': '沪深京 A 股-实时行情'},
    )
    code = Column(String(10), comment='股票代码')
    name = Column(String(20), comment='股票名称')
    latest_time = Column(DateTime, comment='当天最后一次更新时间')
    latest_price = Column(FLOAT, comment='当天最后一次更新价格')
    quote_change = Column(FLOAT, comment='涨跌额')
    ups_downs = Column(FLOAT, comment='涨跌幅')
    volume = Column(Integer, comment='成交量')
    turnover = Column(DECIMAL(40, 4), comment='成交额')
    amplitude = Column(FLOAT, comment='振幅')
    high = Column(FLOAT, comment='最高')
    low = Column(FLOAT, comment='最低')
    open = Column(FLOAT, comment='今开')
    closed = Column(FLOAT, comment='昨收')
    quantity_ratio = Column(FLOAT, comment='量比')
    turnover_rate = Column(FLOAT, comment='换手率')
    pe_dynamic = Column(FLOAT, comment='市盈率-动态')
    pb = Column(FLOAT, comment='市净率')
    date = Column(CHAR(8), comment='日期')


class FundEtfDailyEm(Base):
    """
    东方财富网-天天基金网-基金数据-场内交易基金
    当15点之后更新的数据,latest_price作为当日收盘价
    由于fund_etf_fund_info_em不提供市价(收盘价),
    所以使用auto_macd_params计算式, 不适用此表的数据
    """
    __tablename__ = 'fund_etf_daily_em'
    __table_args__ = (
        PrimaryKeyConstraint('date', 'code'),
        {'comment': "场内交易基金实时行情"},
    )
    code = Column(String(10), comment='基金代码')
    name = Column(String(10), comment='基金简称')
    type = Column(String(10), comment='类型')
    latest_time = Column(String(10), comment='当天最后更新时间')
    latest_price = Column(FLOAT, comment='当天最后一次更新价格')
    date = Column(CHAR(8), comment='日期')


class FundEtfInfoEm(Base):
    __tablename__ = 'fund_etf_info_em'
    __table_args__ = (
        PrimaryKeyConstraint('date', 'code'),
        {'comment': "场内交易基金实时行情"},
    )
    code = Column(String(10), comment='基金代码')
    name = Column(String(10), comment='基金简称')
    nva = Column(String(10), comment='单位净值')
    cum_net = Column(String(10), comment='累计净值')
    ups_downs = Column(String(10), comment='日增长率')
    date = Column(CHAR(8), comment='净值日期')


class SubStocks(Base):
    __tablename__ = 'sub_stocks'
    __table_args__ = (
        PrimaryKeyConstraint('date', 'code'),
        {'comment': "订阅的股票或EFT信息"},
    )
    code = Column(String(10), comment='股票|基金代码')
    name = Column(String(10), comment='股票|基金简称')
    stock_type = Column(Integer, comment='1.股票; 2. 基金')
    is_delete = Column(BOOLEAN, default=False,comment='是否失效')
    date = Column(CHAR(8), comment='日期')


if __name__ == '__main__':
    Base.metadata.create_all(engine)