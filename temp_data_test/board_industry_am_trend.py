# coding=utf-8=

"""
expam 选取上涨板块
"""
import json
import os

import pandas as pd
from stockstats import StockDataFrame
import akshare as ak


def get_test_data(symbol='互联网服务'):
    if os.path.exists(f'./{symbol}.gzip.pickle') is True:
        return pd.read_pickle(f'./{symbol}.gzip.pickle', compression="gzip")
    else:
        data_ = ak.stock_board_industry_hist_em(symbol=symbol)
        data_.to_pickle(f'./{symbol}.gzip.pickle', compression="gzip")
        return data_


class Expma:
    EMA_SHORT = 9
    EMA_LONG = 30

    def __init__(self, api_df: pd.DataFrame, ema_short=None, ema_long=None):

        self.sdf = self.fmt_api_date(api_df)
        self.__ema_short = ema_short if ema_short else Expma.EMA_SHORT
        self.__ema_long = ema_long if ema_long else Expma.EMA_LONG
        self.buy_signal = False
        self.__is_empty = True
        self.buy_data = list()

    @staticmethod
    def fmt_api_date(api_data: pd.DataFrame):
        fmt_st = api_data[['日期', '收盘', '最高', '最低', '成交量']]
        fmt_st.columns = ['date', 'close', 'high', 'low', 'volume']
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
        with open('./back_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(self.buy_data, f, indent=4)

    def back_test(self):
        self._cul_ema_short_line()
        self._cul_ema_long_line()
        self._cul_dif_ema()
        # new_df = self.sdf[['date', 'close', 'ema_short_line', 'ema_long_line', 'dif_ema', 'date']]
        new_df = self.sdf[self.sdf.shape[0] - 365*2:self.sdf.shape[0]]
        # new_df.columns = ['date', 'close', 'ema_short_line', 'ema_long_line', 'dif_ema']
        i = 0
        for i in range(10, new_df.shape[0]):
            mean_day1 = new_df['ema_short_line'][i]
            mean_day2 = new_df['ema_short_line'][i - 1:i].mean()
            mean_day3 = new_df['ema_short_line'][i - 2:i].mean()
            # mean_day10 = new_df['ema_short_line'][i-9:i].mean()
            mean_dif_day1 = new_df['dif_ema'][i]
            mean_dif_day2 = new_df['dif_ema'][i-1:i].mean()
            mean_dif_day3 = new_df['dif_ema'][i - 2:i].mean()
            # mean_dif_day10 = new_df['dif_ema'][i - 9:i].mean()
            if self.__is_empty is True:
                if mean_day1 > mean_day2 > mean_day3 and mean_dif_day1 > mean_dif_day2 > mean_dif_day3:
                    # 空仓且条件符合, 买入
                    # ema_short_line 斜率正， dif 正在由负转正
                    last_buy_item = self.buy_data[-1] if len(self.buy_data) else None
                    rate_increase = 1 if last_buy_item is None \
                        else new_df['close'][i] / last_buy_item['close'] * last_buy_item['rate_increase']
                    self.buy_data.append(
                        self.buy_sell_item(new_df.index[i], new_df['close'][i], rate_increase, is_buy=True))
                    self.__is_empty = False
            else:
                if mean_day1 > mean_day2 > mean_day3 and mean_dif_day1 > mean_dif_day2 > mean_dif_day3:
                    # 满仓且正在上涨, 持有, 否则卖出
                    continue
                else:  # 满仓但有下跌趋势, 卖出, 并计算涨跌幅
                    last_buy_item = self.buy_data[-1] if len(self.buy_data) else None
                    rate_increase = 1 if last_buy_item is None \
                        else new_df['close'][i] / last_buy_item['close'] * last_buy_item['rate_increase']
                    self.buy_data.append(
                        self.buy_sell_item(new_df.index[i], new_df['close'][i], rate_increase, is_buy=False))
        if self.__is_empty is False:  # 满仓条件下, 计算回测结束时涨幅
            last_buy_item = self.buy_data[i] if len(self.buy_data) else None
            rate_increase = 1 if last_buy_item is None \
                else new_df['close'][i] / last_buy_item['close'] * last_buy_item['rate_increase']
            self.buy_data.append(
                self.buy_sell_item(new_df.index[i], new_df['close'][i], rate_increase, is_buy=False, is_end=True))
        self.save_result()


if __name__ == '__main__':
    data = get_test_data()
    ex = Expma(data)
    ex.back_test()
