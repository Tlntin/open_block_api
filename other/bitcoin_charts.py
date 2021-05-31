import pandas as pd
import time
from datetime import datetime
import numpy as np
from tqdm import tqdm
import os


class Bitcoin(object):
    """
    数据下载来源http://api.bitcoincharts.com/v1/csv/
    可以处理成各类时间戳的相关数据
    """
    def __init__(self, interval: int, input_path='./data/krakenUSD.csv'):
        """
        构造函数初始化
        :param interval: int类型，k线间隔，单位为秒，若为15分钟数据，则间隔为15*60
        :param input_path: str类型：原始数据路径
        """
        self.interval = interval
        self.input_path = input_path

    def read_data(self, input_path=None, columns=None):
        """
        简单读取数据，获取数据有多少行，多少列，以及数据开始与结尾
        使用迭代的方法减少内存占用
        :return:
        """
        if input_path is None:
            input_path = self.input_path
        if columns is None:
            columns = ['timestamp', 'price', 'volume']
        df1 = pd.read_csv(input_path, iterator=True, names=columns)
        loop = True
        chunk_size = 200000
        chunk = []
        start_data = None
        end_data = None
        data_length = 0  # 储存数据长度
        start_time = time.time()
        while loop:
            try:
                chunk = df1.get_chunk(chunk_size)
                if data_length == 0:
                    start_data = chunk.iloc[0].values.tolist()
                    print('首行数据为', start_data)
                data_length += len(chunk)
                print('\r当前已读取{}行'.format(data_length), end='')
            except StopIteration:
                loop = False
                print('')
                end_data = chunk.iloc[-1].values.tolist()
                end_time = time.time()
                print('所有数据均处理完成', '用时{:.2f}秒'.format(end_time - start_time))
                # print(end_data)
        return start_data, end_data, data_length

    @staticmethod
    def stamp2time(timestamp: int):
        """
        一个简单的时间戳转字符串
        :param timestamp: int类型， 时间戳
        :return:
        """
        if timestamp > 10**11:
            timestamp = timestamp / 1000
        time_array = datetime.fromtimestamp(timestamp)
        time_str = time_array.strftime('%Y-%m-%d %H:%M:%S')
        return time_str

    def cluster_data(self, output_path='./data/temp.csv'):
        """
        按照时间间隔，对数据进行间隔归类
        :return:
        """
        columns = ['timestamp', 'price', 'volume']
        df1 = pd.read_csv(self.input_path, iterator=True, names=columns)
        loop = True
        chunk_size = 500000  # 一次读取50万，可以根据实际需要调整
        data_length = 0
        start_time = time.time()
        while loop:
            try:
                chunk = df1.get_chunk(chunk_size)
                chunk['new_timestamp'] = chunk['timestamp'].apply(lambda x: int(x // self.interval) * self.interval)
                if data_length == 0:
                    chunk.to_csv(output_path, index=False, mode='w', header=False)
                else:
                    chunk.to_csv(output_path, index=False, mode='a', header=False)
                data_length += len(chunk)
                print('\r当前已处理{}行数据'.format(data_length), end='')
            except StopIteration:
                loop = False
                print('')
                end_time = time.time()
                print('所有数据均处理完成', '用时{:.2f}秒'.format(end_time - start_time))

    def get_k_line(self, input_path='./data/temp.csv', iterator=False, output_path='data/BTC.csv'):
        """
        根据上面的简单归类，计算相应K线，如open, high, lower, close, volume等等

        :return:
        """
        # 如果不迭代
        columns = ['timestamp', 'price', 'volume', 'new_timestamp']
        result_columns = ['date_time', 'open', 'high', 'low', 'close', 'volume']
        if not iterator:
            start_time = time.time()
            print('开始读取数据，请耐心等待')
            df1 = pd.read_csv(input_path, names=columns)
            end_time = time.time()
            print('所有数据读取完成', '用时{:.2f}秒'.format(end_time - start_time))
            # -- 第一种方案，遍历DataFrame --, 预计需要1小时
            result_list = []
            temp_data = []  # 临时二维列表
            for i in tqdm(range(0, len(df1) - 1)):
                temp_data.append(df1.loc[i, :].values.tolist())
                if df1.loc[i, 'new_timestamp'] != df1.loc[i+1, 'new_timestamp']:
                    temp_data = np.array(temp_data)
                    result_list.append([
                        self.stamp2time(df1.loc[i, 'new_timestamp']),   # 获取日期
                        temp_data[0, 1],  # 开盘价
                        temp_data[:, 1].max(),  # 最高价
                        temp_data[:, 1].min(),  # 最低价
                        temp_data[len(temp_data)-1, 1],  # 收盘价
                        temp_data[:, 2].sum()  # 总交易量
                    ])
                    temp_data = []  # 清空临时表,因为下一列要不相等了
            df3 = pd.DataFrame(result_list, columns=result_columns)
            df3.to_csv(output_path, index=False, mode='w', header=True)
            # 第二种方案，使用DataFrame筛选合适的值，然后再做计算,预计需要2h
            # result_list = []
            # start_data, end_data, data_length = btc.read_data('data/temp.csv', columns=columns)
            # start_timestamp = int(start_data[-1])
            # end_timestamp = int(end_data[-1])
            # for timestamp in tqdm(range(start_timestamp, end_timestamp+1, self.interval)):
            #     temp_df = df1[df1.iloc[:, -1] == timestamp]
            #     temp_df = temp_df.reset_index()
            #     if len(temp_df) > 0:
            #         result_list.append([
            #             self.stamp2time(timestamp),  # 获取日期
            #             temp_df.price[0],
            #             temp_df.price.max(),
            #             temp_df.price.min(),
            #             temp_df.price[len(temp_df)-1],
            #             temp_df.volume.sum()
            #         ])
            #     else:
            #         result_list.append([
            #             self.stamp2time(timestamp),  # 获取日期
            #             result_list[-1][1],
            #             result_list[-1][1],
            #             result_list[-1][1],
            #             result_list[-1][1],
            #             0
            #         ])
            # df3 = pd.DataFrame(result_list, columns=result_columns)
            # df3.to_csv(output_path, index=False, mode='w', header=True)
        # 如果迭代的话, 假设使用方案2，这种方案需要的时间最短
        else:
            loop = True
            chunk_size = 100000
            df1 = pd.read_csv(input_path, names=columns, iterator=iterator)
            last_df = []
            data_length = 0
            while loop:
                try:
                    chunk = df1.get_chunk(chunk_size)
                    if len(last_df) == 0:
                        df2 = chunk.copy()
                        df2 = df2.reset_index()
                    else:
                        df2 = pd.concat([last_df, chunk], axis=0)
                    start_timestamp = int(df2.iloc[0, -1])
                    end_timestamp = int(df2.iloc[len(df2)-1, -1])
                    result_list = []  # 储存结果
                    for timestamp in tqdm(range(start_timestamp, end_timestamp, self.interval)):
                        temp_df = df2[df2.iloc[:, -1] == timestamp]
                        temp_df = temp_df.reset_index()
                        if len(temp_df) > 0:
                            result_list.append([
                                self.stamp2time(timestamp),  # 获取日期
                                round(temp_df.price[0], 4),
                                round(temp_df.price.max(), 4),
                                round(temp_df.price.min(), 4),
                                round(temp_df.price[len(temp_df)-1], 4),
                                round(temp_df.volume.sum(), 8)
                            ])
                        else:
                            result_list.append([
                                self.stamp2time(timestamp),  # 获取日期
                                result_list[-1][1],
                                result_list[-1][1],
                                result_list[-1][1],
                                result_list[-1][1],
                                0
                            ])
                    last_df = df2[df2.iloc[:, -1] == end_timestamp]
                    df3 = pd.DataFrame(result_list, columns=result_columns)
                    if data_length == 0:
                        df3.to_csv(output_path, index=False, mode='w', header=True)
                    else:
                        df3.to_csv(output_path, index=False, mode='a', header=False)
                    data_length += len(chunk)
                    print('当前已处理{}行数据'.format(data_length))
                except StopIteration:
                    loop = False  # 循环结束


if __name__ == '__main__':
    btc = Bitcoin(15*60)
    # start_data, end_data, data_length = btc.read_data('./data/temp.csv')
    # start_timestamp = int(start_data[-1])
    # end_timestamp = int(end_data[-1])
    # list1 = list(range(start_timestamp, end_timestamp+1, btc.interval))
    # print('理论应该有{}条数据'.format(len(list1)))
    # 第一步，聚类
    # btc.cluster_data()
    # 第二步，汇总
    btc.get_k_line(iterator=True, output_path='data/BTC.csv')