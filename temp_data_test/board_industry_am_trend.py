# coding=utf-8=

"""
expam 选取上涨板块
"""
import json
import os
import time
import datetime

import pandas as pd
from stockstats import StockDataFrame
import akshare as ak


def get_industry_data(symbol='互联网服务'):
    if os.path.exists(f'./{symbol}.gzip.pickle') is True:
        return pd.read_pickle(f'./{symbol}.gzip.pickle', compression="gzip"), symbol
    else:
        data_ = ak.stock_board_industry_hist_em(symbol=symbol)
        data_.to_pickle(f'./{symbol}.gzip.pickle', compression="gzip")
        return data_, symbol


def get_single_stock(symbol='000001', date='20200101'):
    end_date = time.strftime('%Y%m%d')
    if os.path.exists(f'./{symbol}_{end_date}.gzip.pickle') is True:
        return pd.read_pickle(f'./{symbol}_{end_date}.gzip.pickle', compression="gzip"), symbol
    else:
        data_ = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=date, adjust= "qfq")
        data_.to_pickle(f'./{symbol}_{end_date}.gzip.pickle', compression="gzip")
        return data_, symbol


def get_single_index(symbol=''):
    end_date = time.strftime('%Y%m%d')
    if os.path.exists(f'./index_{symbol}_{end_date}.gzip.pickle') is True:
        return pd.read_pickle(f'./index_{symbol}_{end_date}.gzip.pickle', compression="gzip"), symbol
    else:
        data_ = ak.stock_zh_index_daily(symbol=symbol)
        data_.to_pickle(f'./index_{symbol}_{end_date}.gzip.pickle', compression="gzip")
        return data_, symbol


class Expma:

    def __init__(self, api_df: pd.DataFrame, symbol: str,ema_short=None, ema_long=None):

        self.symbol = symbol
        self.api_df = api_df
        self.sdf = self.fmt_api_date(api_df)
        self.__ema_short = ema_short if ema_short else StockDataFrame.MACD_EMA_SHORT
        self.__ema_long = ema_long if ema_long else StockDataFrame.MACD_EMA_LONG
        # self.__ema_ = MACD_EMA_SIGNAL
        self.buy_signal = False
        self.__is_empty = True
        self.buy_data = list()
        self.is_first_buy = True

    @staticmethod
    def fmt_api_date(api_data: pd.DataFrame):
        if '日期' in api_data.columns:
            fmt_st = api_data[['日期', '收盘', '最高', '最低', '成交量']]
            fmt_st.columns = ['date', 'close', 'high', 'low', 'volume']
        elif 'date' in api_data.columns:
            fmt_st = api_data[['date', 'close', 'high', 'low', 'volume']]
            # fmt_st.columns = ['date', 'close', 'high', 'low', 'volume']
            fmt_st['date'].astype(dtype='str')
        else:
            raise KeyError('字段不匹配')
        return StockDataFrame(fmt_st)
    @property
    def ema_short(self):
        return self.__ema_short

    @property
    def ema_long(self):
        return self.__ema_long

    @ema_short.setter
    def ema_short(self, ema_short):
        if isinstance(ema_short, int):
            self.__ema_short = ema_short
        else:
            raise ValueError

    @ema_long.setter
    def ema_long(self, ema_long):
        if isinstance(ema_long, int):
            self.__ema_short = ema_long
        else:
            raise ValueError

    @staticmethod
    def buy_sell_item(date, close, rate_increase, is_buy: bool, is_end=False):
        return {
            'date': date,
            'close': close,
            'rate_increase': rate_increase,
            'is_buy': is_buy,
            'is_end': is_end
        }

    def _cul_ema_short_line(self):
        self.sdf['ema_short_line'] = self.sdf._ema(self.sdf['close'], self.ema_short)

    def _cul_ema_long_line(self):
        self.sdf['ema_long_line'] = self.sdf._ema(self.sdf['close'], self.ema_long)

    def _cul_dif_ema(self):
        self.sdf['dif_ema'] = self.sdf['ema_short_line'] - self.sdf['ema_long_line']

    def is_buy_signal(self):
        pass

    def save_result(self):
        with open(f'./{self.symbol}_back_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(self.buy_data, f, indent=4)

    def back_test2(self):
        # macd 回测
        new_df = self.sdf[self.sdf.shape[0] - min(600, self.sdf.shape[0]):self.sdf.shape[0]]
        i = 0
        for i in range(new_df.shape[0] - min(260, new_df.shape[0]), new_df.shape[0]):
            macd = new_df['macd'][i]
            macd1 = new_df['macd'][i-1]
            macds = new_df['macds'][i]
            macdh = new_df['macdh'][i]
            macdh1 = new_df['macdh'][i - 1]

            if self.__is_empty is True:
                if macdh >= 0 >= macdh1 or 0 < macd < macdh:
                    # 空仓且条件符合, 买入
                    # ema_short_line 斜率正， dif 正在由负转正
                    last_buy_item = self.buy_data[-1] if len(self.buy_data) else None
                    rate_increase = 1 if last_buy_item is None else last_buy_item['rate_increase']
                    self.buy_data.append(
                        self.buy_sell_item(str(new_df.index[i]), new_df['close'][i], rate_increase, is_buy=True))
                    self.__is_empty = False
            else:
                # if macdh > macdh1 and close > close1:
                #     # 满仓且正在上涨, 持有, 否则卖出
                #     continue
                # if (macdh < macdh1 and (new_df['macdh'][i-2] <= 0 or new_df['macdh'][i-3]<=0))\
                #         or (macdh <= 0):  # macdh转正三天
                # if macdh <= 0 or (macdh < macdh1 and macd < macd1):
                if macdh <= 0:
                    last_buy_item = self.buy_data[-1] if len(self.buy_data) else None
                    rate_increase = 1 if last_buy_item is None \
                        else new_df['close'][i] / last_buy_item['close'] * last_buy_item['rate_increase']
                    self.buy_data.append(
                        self.buy_sell_item(str(new_df.index[i]), new_df['close'][i], rate_increase, is_buy=False))
                    self.__is_empty = True
        if self.__is_empty is False:  # 满仓条件下, 计算回测结束时涨幅
            last_buy_item = self.buy_data[-1] if len(self.buy_data) else None
            rate_increase = 1 if last_buy_item is None \
                else new_df['close'][i] / last_buy_item['close'] * last_buy_item['rate_increase']
            self.buy_data.append(
                self.buy_sell_item(str(new_df.index[i]), new_df['close'][i], rate_increase, is_buy=False, is_end=True))
        self.save_result()


if __name__ == '__main__':
    symbol = 'sz399997'
    # symbol = '汽车整车'
    # data, symbol = get_single_stock(symbol)
    # data, symbol = get_industry_data(symbol)
    data, symbol = get_single_index(symbol)
    ex = Expma(data, symbol)
    ex.back_test2()
