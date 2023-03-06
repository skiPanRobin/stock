# -*- coding: UTF-8 -*-
"""
@Project ：income_track 
@Author  ：NewBin
@Date    ：2023/3/6 9:05 
"""
import json

from mysql_tool import MysqlTool


class SubStocks:

    def __init__(self):
        self.__mt = MysqlTool()

    def get_stocks(self):
        with self.__mt.cursor as cur:
            cur.execute("select code, name, stock_type from sub_stocks where is_delete=0")
            return cur.fetchall()


    def _read_local_file(self):
        with open('.\sub_stocks\sub_stocks01.json', 'r', encoding='utf-8') as f:
            j = json.load(fp=f)
            for items in j:
                yield items.keys


    def write_stocks(self):
        with self.__mt.cursor as cur:

                pass
