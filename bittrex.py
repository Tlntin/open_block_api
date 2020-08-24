import pandas as pd
import requests
from pprint import pprint
import datetime
import time
from random import random
import os


class Data(object):
    """
    基于https://bittrex.github.io/构建的api模块
    方便下载bittrex交易所历史K线数据
    """
    def __init__(self, symbol, interval):
        """
        初始化
        :param symbol: 交易对名称，比如"BTC/USDT"
        :param interval: 交易间隔，支持5分钟："MINUTE_5", 1小时："HOUR_1"， 1天："DAY_1"
        """
        if '/' not in symbol and '_' not in symbol:
            raise Exception('你的交易对可能写的不对，可以写成BTC/USDT或者BTC_USDT')
        if interval not in ['MINUTE_5', 'HOUR_1', 'DAY_1']:
            raise Exception('你的交易间隔可能有毛病，看看说明文档再继续吧')
        self.symbol = symbol.replace('/', '-').replace('_', '-')
        self.interval = interval

    def get_k_line(self, date_time):
        """
        获取bittrex的历史k线数据
        :param date_time: 日期，如果是5分钟线，则格式为"%Y/%m/%d"，如果是1h线，则格式为"%Y/%m"，如果为1d线，则为"%Y"
        :return: 处理好的DataFrame
        """
        url = 'https://api.bittrex.com/v3/markets/{}/candles/{}/historical/{}'.format(self.symbol,
                                                                                      self.interval,
                                                                                      date_time)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = self.parse_data(data)
            return df
        else:  # 如果因为周期不足1年导致数据无法返回，那么就返回当天到历史数据1年的数据
            url = 'https://api.bittrex.com/v3/markets/{}/candles/{}/recent'.format(self.symbol,
                                                                                   self.interval)
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                df = self.parse_data(data)
                return df
            else:
                return None

    @staticmethod
    def parse_data(raw_data):
        """
        利用pandas对数据进行简单处理
        :param raw_data: 原始数据
        :return:
        """
        data = [list(da.values()) for da in raw_data]
        columns = list(raw_data[0].keys())
        columns[0] = 'time'
        df = pd.DataFrame(data, columns=columns)
        df.time = df.time.apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(x, '%Y-%m-%dT%H:%M:%SZ')))
        df.time = pd.to_datetime(df.time)
        return df

    def get_all_k_line(self, start_time, end_time):
        """
        获取所有k线数据
        :param start_time: 开始时间，格式参考 "%Y-%m-%d %H:%M:%S"
        :param end_time: 结束时间，格式参考 "%Y-%m-%d %H:%M:%S"
        :return:
        """
        now_time = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
        if end_time > now_time:
            raise Exception('你的结束时间貌似比现在最新时间还新，改改吧')
        # 简单改变样式
        start_time_new = time.strftime("%Y-%m-%d", time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
        end_time_new = time.strftime("%Y-%m-%d", time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
        time_interval = pd.date_range(start_time_new, end_time_new, freq='1D').tolist()
        # 如果为5分钟
        if self.interval == 'MINUTE_5':
            # 格式化为%Y/%m/%d格式
            time_interval = [t.strftime('%Y/%m/%d') for t in time_interval]
        # 如果为1小时
        elif self.interval == 'HOUR_1':
            # 格式化为%Y/%m
            time_interval = [t.strftime('%Y/%m') for t in time_interval]
        # 如果为1d
        elif self.interval == 'DAY_1':
            time_interval = [t.strftime('%Y') for t in time_interval]
        # 对时间间隔进去去重
        dict1 = {}
        for t in time_interval:
            dict1[t] = dict1.get(t, 0)
        time_interval = list(dict1.keys())
        df = self.download_many_kline(time_interval)
        df = self.filter_many_kline(df, start_time=start_time, end_time=end_time)
        if isinstance(df, pd.DataFrame):
            df.to_csv('./data/bittrex_{}_{}_from_{}_to_{}.csv'.format(
                self.symbol, self.interval, start_time, end_time))
        return df

    def download_many_kline(self, time_interval: list):
        """
        批量下载K线，然后返回DataFrame格式
        :param time_interval: 时间间隔
        """
        df = None
        for i in range(len(time_interval)):
            print('正在下载{}的数据'.format(time_interval[i]))
            temp_df = self.get_k_line(time_interval[i])
            if temp_df is not None:
                if i == 0:
                    df = temp_df
                else:
                    df = pd.concat([df, temp_df], axis=0)
            time.sleep(random() + 0.2)
        return df

    def filter_many_kline(self, raw_df: pd.DataFrame, start_time: str, end_time: str):
        """
        根据获取到的数据，以及时间间隔，以及开始和结束时间，筛选出自己想要的那一部分数据
        :param raw_df: 原始dataFrame数据
        :param start_time: 开始时间，格式参考 "%Y-%m-%d %H:%M:%S"
        :param end_time: 结束时间，格式参考 "%Y-%m-%d %H:%M:%S"
        """
        raw_df = raw_df.drop_duplicates(subset=['time'])  # 删除重复值
        raw_df = raw_df.reset_index()
        raw_df.pop('index')
        if self.interval == 'DAY_1':
            start_time = time.strftime("%Y-%m-%d", time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
            end_time = time.strftime("%Y-%m-%d", time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
            time_interval = pd.date_range(start_time, end_time, freq='1D').tolist()
            # time_interval = [t.strftime('%Y-%m-%d') for t in time_interval]
        elif self.interval == 'HOUR_1':
            time_interval = pd.date_range(start_time, end_time, freq='1H').tolist()
        else:
            time_interval = pd.date_range(start_time, end_time, freq='5min').tolist()
        # print(time_interval)
        result_index = []
        for i in range(len(raw_df)):
            time_str = raw_df.loc[i, 'time']
            if time_str in time_interval:
                result_index.append(i)
        df = raw_df.loc[result_index]
        df = df.reset_index()
        df.pop('index')
        return df


if __name__ == '__main__':
    if not os.path.exists('data'):
        os.mkdir('data')
    da = Data('BTC/USDT', 'MINUTE_5')  # MINUTE_5，HOUR_1，DAY_1
    df1 = da.get_all_k_line('2020-07-01 01:00:00', '2020-07-04 01:00:00')
    # df1 = da.get_k_line('2020')
    pprint(df1)
