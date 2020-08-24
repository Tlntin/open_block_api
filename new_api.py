from pprint import pprint
import pandas as pd
import time
from datetime import datetime
from random import random
from raw_api import RawApi


class NewApi(RawApi):
    """
    编写了一个新api，方便获取所有币种历史数据信息
    """
    def __init__(self, exchange_id: str, symbol: str):
        """
        初始化构造函数
        :param exchange_id: 交易所id，可以通过NewApi.get_exchange()获取所有交易所名称
        :param symbol: 交易对名称，建议大写加斜线，比如BTC/USDT
        """
        self.exchange_id = exchange_id
        if self.exchange_id not in self.get_exchange():
            raise Exception('exchange_id may be wrong, please check it')
        symbol = symbol.upper()
        if '_' in symbol:
            symbol_list = symbol.split('_')
        elif '/' in symbol:
            symbol_list = symbol.split('/')
        else:
            raise Exception('Symbol写法有误，请参造BTC/USDT这种写法去写')
        # 需要将Symbol格式化为原始api提供的id格式
        base_symbol = symbol_list[0]  # 基础交易币种，比如比特币
        quote_symbol = symbol_list[1]  # 转换结算币种，比如USDT
        market_list = self.get_market(self.exchange_id, limit=500)
        # 获取基础币种id和结算币种id
        self.base_id = [data['baseId'] for data in market_list if data['baseSymbol'] == base_symbol][0]
        self.quote_id = [data['quoteId'] for data in market_list if data['quoteSymbol'] == quote_symbol][0]
        self.symbol = symbol
        print('api初始化完成')

    @staticmethod
    def time2stamp(time_str: str):
        """
        编写一个简单的时间转时间戳函数
        :param time_str: 时间，建议格式为"%Y-%m-%d %H:%M:S"
        :return:
        """
        if '-' not in time_str:
            raise Exception('You time format may be wrong! You should do like "%Y-%m-%d %H:%M:%S",'
                            ' such as ""2020-01-02 11:00:00')
        time_array = time.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        time_stamp = int(time.mktime(time_array)) * 1000
        return time_stamp

    @staticmethod
    def interval2timestamp(interval):
        """
        编写一个时间间隔转时间戳的函数
        :param interval: 时间间隔可选择m1, m5, m15, m30, h1, h2, h4, h8, h12, d1, w1
        :return:
        """
        stamp = 1
        if interval == 'm1':
            stamp = 60
        elif interval == 'm15':
            stamp = 60 * 15
        elif interval == 'm30':
            stamp = 60 * 30
        elif interval == 'h1':
            stamp = 60 * 60
        elif interval == 'h2':
            stamp = 60 * 60 * 2
        elif interval == 'h4':
            stamp = 60 * 60 * 4
        elif interval == 'd1':
            stamp = 60 * 60 * 24
        elif interval == 'w1':
            stamp = 60 * 60 * 24 * 7
        else:
            raise Exception('interval is error')
        return stamp * 1000

    def get_k_lines(self, interval: str, start_time: str = None, end_time: str = None):
        """
        获取K线相关数据，开始时间与结束时间可以为空
        :param interval: 间隔，可选择	m1, m5, m15, m30, h1, h2, h4, h8, h12, d1, w1
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        if interval not in "m1, m5, m15, m30, h1, h2, h4, h8, h12, d1, w1".split(', '):
            raise Exception('you interval may be error\n,\
            interval just can be one of the" m1, m5, m15, m30, h1, h2, h4, h8, h12, d1, w1"')
        if start_time is None or end_time is None:
            print(self.exchange_id, interval, self.base_id, self.quote_id)
            df = self.get_candles(self.exchange_id, interval, self.base_id, self.quote_id)
            print(df.head())
        else:
            start_timestamp = self.time2stamp(start_time)  # 获取开始时间戳
            end_timestamp = self.time2stamp(end_time)  # 获取结束时间戳
            interval_timestamp = self.interval2timestamp(interval)  # 获取间隔时间戳
            n = int((end_timestamp - start_timestamp) / interval_timestamp)  # 计算可以获取的总信息条数
            print('预计本次获取{}条数据'.format(n))
            # 如果一次性获取的信息比较少
            if n <= 24 * 12:
                df = self.get_candles(self.exchange_id, interval, self.base_id, self.quote_id,
                                      start_timestamp, end_timestamp)
                print(df)
            else:
                one_time = 24 * 12  # 每次获取的数据数量
                times = int(n / one_time)
                another = n % one_time
                result_df = None  # 这个用于汇总所有的dataFrame
                for i in range(1, times+1):
                    temp_start_time = datetime.fromtimestamp(int(start_timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    temp_end_time = datetime.fromtimestamp(int(start_timestamp +
                                                               1 * interval_timestamp *\
                                                               one_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    temp_df = self.get_candles(self.exchange_id, interval, self.base_id, self.quote_id,
                                               start_timestamp, start_timestamp + 1 * interval_timestamp * one_time)
                    if temp_df is not None:
                        print('本次数据开始时间：{}, 结束时间：{}, 共获取数据{}条'.format(temp_start_time,
                                                                      temp_end_time, len(temp_df)))
                        if i == 0:
                            result_df = temp_df
                        else:
                            result_df = pd.concat([result_df, temp_df], axis=0)
                    start_timestamp += interval_timestamp * one_time  # 这里必须加1个间隔时间戳
                    time.sleep(random())
                if another != 0:
                    temp_start_time = datetime.fromtimestamp(int(start_timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    temp_end_time = datetime.fromtimestamp(int(end_timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    temp_df = self.get_candles(self.exchange_id, interval, self.base_id, self.quote_id,
                                               start_timestamp, end_timestamp)
                    if temp_df is not None:
                        print('本次数据开始时间：{}, 结束时间：{}, 共获取数据{}条'.format(temp_start_time,
                                                                      temp_end_time, len(temp_df)))
                        result_df = pd.concat([result_df, temp_df], axis=0)
                print('所有文件均下载完毕，已储存在py文件同路径')
                result_df.to_csv('{}_{}_{}.csv'.format(self.exchange_id, self.symbol.replace('/', ''), interval),
                                 index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    # pprint(NewApi.get_exchange())
    api = NewApi('huobi', 'BTC/USDT')
    api.get_k_lines('h1', '2017-01-01 01:00:00', '2020-08-20 01:00:00')
