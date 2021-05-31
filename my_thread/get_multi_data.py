import requests
import yaml
import os
from pprint import pprint
import pandas as pd
from utils.my_tools import interval2timestamp, stamp2time
from my_thread.thread import MyThread
from tqdm import tqdm


class GetMultiData(object):
    """
    利用多线程下载数据
    """
    def __init__(self, exchange: str, interval, base_id: str, quote_id: str, start_ts: int, end_ts: int):
        """
        初始化构造函数
        :param exchange: 交易所名称，比如huobi
        :param interval: 间隔，比如m15,h1, d1
        :param base_id: 底层币，比如usdt
        :param quote_id: 待交换币，比如btc
        :param start_ts: 开始时间，int,13位时间戳
        :param end_ts: 结束时间，int, 13位时间戳
        """
        self.parent_dir = os.path.dirname(os.path.dirname(__file__))
        yaml_path = os.path.join(self.parent_dir, "config.yaml")
        with open(yaml_path) as f:
            self.yaml_dict = yaml.safe_load(f)
        # 构建请求字典
        self.param_dict = {
            'exchange': exchange,
            'interval': interval,
            'baseId': base_id,
            'quoteId': quote_id,
        }
        self.base_id = base_id
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.interval = interval
        self.ts_interval, self.new_interval = interval2timestamp(self.interval)
        print("交易所名称：{},币种名称：{}，数据间隔为：{}".format(exchange, base_id, self.new_interval))
        print("开始时间：", stamp2time(start_ts), ",结束时间：", stamp2time(end_ts))
        assert self.start_ts > 10 ** 12
        assert self.end_ts > 10 ** 12

    def get_time_list(self):
        """
        获取一个时间序列列表，方便接下来的多线程获取数据
        :return:
        """
        # print(ts_interval)
        once_num = self.yaml_dict["once_num"]
        total_num = int((self.end_ts - self.start_ts) / self.ts_interval)  # 计算可以获取的总信息条数
        if total_num < once_num:
            time_list = [self.start_ts, self.end_ts]
        else:
            time_list = []
            temp_ts = self.start_ts
            while temp_ts < self.end_ts:
                time_list.append(temp_ts)
                temp_ts += self.ts_interval * once_num
            else:
                time_list.append(self.end_ts)
        return time_list

    def get_once_data(self, start_ts, end_ts):
        """
        获取单次数据
        :return:
        """
        timeout = 20
        for i in range(4):
            try:
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                # 判断是否开启代理
                if bool(self.yaml_dict["proxy"]):
                    proxies = {self.yaml_dict["proxy_type"]: self.yaml_dict["proxy_url"]}
                    s.proxies = proxies
                # 正式请求
                url = 'https://api.coincap.io/v2/candles'
                params = self.param_dict
                # 判断是否为历史数据
                if start_ts is not None and end_ts is not None:
                    params["start"] = start_ts
                    params["end"] = end_ts
                response = s.get(url, params=params, timeout=timeout)
                if response.status_code == 200:
                    data = response.json().get('data', False)
                    if bool(data):
                        data = self.parse_data(data)
                        s.close()
                        return data
                    else:
                        s.close()
                        print('该交易所没有你想要的数据，换一个交易所试试吧')
                        return None
            except Exception as err:
                # 写入到log中
                file_name = "requests_log.txt"
                log_path = os.path.join(self.parent_dir, self.yaml_dict["log_dir"], file_name)
                if not os.path.exists(log_path):
                    f = open(log_path, "wt", encoding="utf-8")
                else:
                    f = open(log_path, "at", encoding="utf-8")
                f.write(f"warning! symbol:{self.base_id}, interval:{self.interval}, start:{start_ts}, end_ts:{end_ts}:\n"\
                        + str(err) + "\n\n")
                f.close()
                timeout += 20

    @staticmethod
    def parse_data(data):
        """
        对数据做一些处理，变成dataFrame格式
        :return:
        """
        data1 = [list(da.values()) for da in data]
        data1 = [[float(d) for d in da1] for da1 in data1]
        df = pd.DataFrame(data1, columns=data[0].keys())
        time_list = df.period.apply(lambda x: stamp2time(x))
        df.insert(0, 'time', time_list)
        df.pop('period')
        return df

    def get_temp_multi_df(self, start_index, time_list, func):
        """
        获取单轮多线程后的数据，防止因为某个线程数据挂了导致的数据获取不全
        :param start_index:
        :param time_list:
        :param func: 执行的函数
        :return:
        """
        multi_num = self.yaml_dict["multi_num"]
        end_num = len(time_list)
        job_list = []
        total_num = 0
        for ii in range(multi_num):
            if start_index + ii + 1 < end_num:
                s_ts = time_list[start_index + ii]
                e_ts = time_list[start_index + ii + 1]
                temp_num = int((e_ts - s_ts) / self.ts_interval)  # 统计理论获取的数量
                total_num += temp_num
                # print(s_ts, e_ts)
                # print(stamp2time(s_ts), stamp2time(e_ts))
                # 构建多线程
                job = MyThread(func, args=(s_ts, e_ts))
                job_list.append(job)
            else:
                break
        # 正式开始多线程
        for job2 in job_list:
            job2.start()
            job2.join()
        # 获取多线程结果
        temp_result_df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        for job3 in job_list:
            temp_df = job3.get_result()
            if temp_df is not None:
                if isinstance(temp_df, pd.DataFrame):
                    temp_result_df = temp_result_df.append(temp_df)
                else:
                    raise Exception("某个分支线程遇到错误，请重新运行")
        temp_result_df = temp_result_df.sort_values(by="time")  # 以防万一，还是按时间排序一下
        return temp_result_df, total_num

    def get_multi_data(self, time_list: list, func):
        """
        利用多线程批量快速获取数据
        :return:
        """
        multi_num = self.yaml_dict["multi_num"]
        end_num = len(time_list)
        result_df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        data_iter = tqdm(range(0, end_num, multi_num))
        for index in data_iter:
            start_ts = time_list[index]
            temp_result_df, once_num = self.get_temp_multi_df(index, time_list, func)
            if temp_result_df is not None:
                result_df = result_df.append(temp_result_df)
                data_iter.set_description("理论获取：{} | 本次获取：{}，累计：{}，当前时间：{}"\
                                          .format(once_num, len(temp_result_df), len(result_df), stamp2time(start_ts)))
            else:
                raise Exception("当前没有获取到任何数据，请检查配置文件")
        print("\n")
        return result_df
    
    def run(self):
        time_list = self.get_time_list()
        result_df = self.get_multi_data(time_list, func=self.get_once_data)
        return result_df


if __name__ == '__main__':
    multi_dict = GetMultiData('huobi', 'm15', 'bitcoin', 'tether', 1570813200000, 1570986000000)
    result_df1 = multi_dict.run()
    print(result_df1)
    # time_list1 = multi_dict.get_time_list()
    # print(time_list1)
    # # time_data = [stamp2time(t) for t in time_list1]
    # # print(time_data)
    # for i in range(len(time_list1)-1):
    #     st = time_list1[i]
    #     et = time_list1[i+1]
    #     temp_data = multi_dict.get_once_data(st, et)
    #     print(temp_data.columns)
    #     print(temp_data)
    #     break
    # SELECT date_time, COUNT(0) as times FROM huobi GROUP BY date_time HAVING COUNT(date_time) > 1;