import pandas as pd
from stockstats import wrap, StockDataFrame
import akshare as ak


def test1():
    stock = pd.read_pickle('./2023-02-06_000056_all.gzip.pickle', compression="gzip")
    print(stock.head(1), type(stock))
    fmt_st = stock[['日期', '收盘', '最高', '最低',  '成交量']]
    fmt_st.columns = ['date', 'close', 'high', 'low', 'volume']
    # stockStat = wrap.StockDataFrame.retype(stock)
    sd = StockDataFrame(fmt_st)
    # sd.set
    df = wrap(stock)
    print(df.head(1))

def test2():
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000056", period="daily")
    stock_zh_a_hist_df.to_pickle('./2023-02-06_000056_all.gzip.pickle', compression="gzip")
    df = wrap(stock_zh_a_hist_df)
    df.to_pickle('./2023-02-06_000056_all_wrap.gzip.pickle', compression="gzip")
    print(stock_zh_a_hist_df.head(1))
    print(df.head(1))



if __name__ == '__main__':
    test1()
