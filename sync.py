from utils.sql import MySQL
from tqdm import tqdm
import os
from datetime import datetime
import yaml
from utils.my_tools import time2stamp, interval2timestamp, stamp2time
from utils.new_api import NewApi


parent_dir = os.path.dirname(__file__)
yaml_path = os.path.join(parent_dir, "config.yaml")
with open(yaml_path) as f:
    yaml_dict = yaml.safe_load(f)


class Sync(object):
    """
    用于同步数据
    """
    def __init__(self, exchange_id: str, symbol: str, interval: str):
        """
        :param exchange_id: 交易所名称
        :param symbol: 交易对信息
        :param interval: 获取的时间间隔
        """
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.interval = interval
        self.ts_interval, self.new_interval = interval2timestamp(interval)
        start_time = yaml_dict["start_time"]
        end_time = yaml_dict["end_time"]
        self.start_timestamp, self.end_timestamp = self.sync_timestamp(start_time, end_time)
        print("交易所：{}，交易对：{}，交易间隔：{}".format(self.exchange_id, self.symbol, self.interval))
        # print(f"开始时间戳为：{self.start_timestamp}，与结束时间戳为：{self.end_timestamp}")
        print("开始时间：{}, 结束时间：{}".format(stamp2time(self.start_timestamp), stamp2time(self.end_timestamp)))

    def sync_timestamp(self, start_time, end_time):
        """
        同步开始时间与结束时间
        :param start_time
        :param end_time
        """
        # -- 设定开始时间 -- #
        mysql = MySQL()
        if not mysql.is_exists_table(self.symbol):  # 根据币种名称创表
            mysql.create_table(self.symbol)
        db_last_time = mysql.query_last_date(self.symbol, self.new_interval)
        # print(db_last_time)
        mysql.cursor.close()
        mysql.db.close()
        if start_time is None and db_last_time is None:
            raise Exception(f'{self.exchange_id}数据库,{self.symbol}交易对,{self.interval}间隔；\
            还没有最新时间，请设定一个起始时间')
        elif db_last_time is not None and start_time is None:
            start_timestamp = db_last_time + self.ts_interval
        elif start_time is not None and db_last_time is None:
            start_timestamp = time2stamp(start_time)
        else:
            start_timestamp = db_last_time + self.ts_interval
        # -- 设定结束时间 -- #
        if end_time is None:
            end_day = datetime.now().date()
            end_time = end_day.strftime('%Y-%m-%d %H:%M:%S')
            end_timestamp = time2stamp(end_time)
        else:
            end_timestamp = time2stamp(end_time)
        return start_timestamp, end_timestamp

    def run(self):
        api = NewApi(self.exchange_id, self.interval, self.symbol, self.start_timestamp, self.end_timestamp)
        api.run()


if __name__ == '__main__':
    exchange_id1 = yaml_dict["exchange"]  # 交易所名称
    symbol_list = yaml_dict["symbol_list"]  # 交易对列表
    interval_list = yaml_dict["interval_list"]  # 交易间隔对
    for symbol1 in symbol_list:
        for interval1 in interval_list:
            sync = Sync(exchange_id1, symbol1, interval1)
            sync.run()
