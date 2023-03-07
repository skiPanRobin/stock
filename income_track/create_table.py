# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/7 18:39 
"""
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, FLOAT, DECIMAL

from mysql_tool import MysqlTool as mt

uri = f'mysql+pymysql://{mt.user}:{quote_plus(mt.password)}@{mt.host}:{mt.port}/{mt.db}?charset={mt.charset}'
engine = create_engine(url=uri)
Base = declarative_base()


class StockZhAhName(Base):
    __tablename__ = 'stock_zh_ah_name'

    code = Column(String(10), primary_key=True)
    name = Column(String(20))
    latest_time = Column(DateTime)
    latest_price = Column(FLOAT)
    quote_change = Column(FLOAT)
    ups_downs = Column(FLOAT)
    volume = Column(FLOAT)
    turnover = Column(FLOAT)
    amplitude = Column(FLOAT)
    high = Column(FLOAT)
    low = Column(FLOAT)
    open = Column(FLOAT)
    closed = Column(FLOAT)
    quantity_ratio = Column(FLOAT)
    turnover_rate = Column(FLOAT)
    pe_dynamic = Column(FLOAT)
    pb = Column(FLOAT)
    date = Column(FLOAT)


