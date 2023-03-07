# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/7 18:39 
"""
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, FLOAT, DECIMAL, CHAR

from mysql_tool import MysqlTool as mt

engine = create_engine(url=mt.uri)
Base = declarative_base()


class StockZhAhName(Base):
    __tablename__ = 'stock_zh_ah_name'

    code = Column(String(10), comment='代码')
    name = Column(String(20), comment='股票名称')
    latest_time = Column(DateTime, comment='当天最后一次更新时间')
    latest_price = Column(FLOAT, comment='当天最后一次更新价格')
    quote_change = Column(FLOAT, comment='换手率')
    ups_downs = Column(FLOAT, comment='')
    volume = Column(Integer)
    turnover = Column(DECIMAL(40, 4))
    amplitude = Column(FLOAT)
    high = Column(FLOAT)
    low = Column(FLOAT)
    open = Column(FLOAT)
    closed = Column(FLOAT)
    quantity_ratio = Column(FLOAT)
    turnover_rate = Column(FLOAT)
    pe_dynamic = Column(FLOAT)
    pb = Column(FLOAT)
    date = Column(CHAR(8))


