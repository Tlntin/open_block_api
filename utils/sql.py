import pymysql
from datetime import datetime
import yaml
import os


class MySQL(object):
    def __init__(self):
        self.parent_dir = os.path.dirname(os.path.dirname(__file__))
        yaml_path = os.path.join(self.parent_dir, "config.yaml")
        with open(yaml_path) as f:
            self.yaml_dict = yaml.safe_load(f)
        self.db = pymysql.connect(**self.yaml_dict["db_config"])
        self.cursor = self.db.cursor()
        # exchange = self.yaml_dict["exchange"]
        # result = self.is_exists_table(exchange)
        # if result is None:
        #     self.create_table(exchange)

    def is_exists_table(self, table_name):
        sql1 = "show tables like '{}'".format(table_name)
        self.cursor.execute(sql1)
        result = self.cursor.fetchone()
        return result

    def create_table(self, table_name):
        sql = """CREATE TABLE IF NOT EXISTS `{}`(
        symbol VARCHAR(255),
        interval_type VARCHAR(255),
        date_time DATETIME,
        time_stamp BIGINT,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume Double,
        PRIMARY KEY (time_stamp, interval_type)
        )
        """.format(table_name)
        self.cursor.execute(sql)
        self.db.commit()
        print('{}表格创建成功'.format(table_name))

    def insert_table(self, table_name, data):
        # print('开始插入{},估计有{}条数据'.format(table_name, len(data)))
        sql1 = f"INSERT INTO `{table_name}` VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.executemany(sql1, data)
        self.db.commit()
        # print(f'{table_name}数据插入成功')

    def query_last_date(self, table_name, interval_type):
        """
        获取最新日期
        :param table_name: 交易对名称
        :param interval_type: 时间间隔，m15或者h1
        """
        sql1 = f"""SELECT time_stamp FROM `{table_name}` \
         WHERE interval_type="{interval_type}" ORDER BY time_stamp DESC LIMIT 1"""
        self.cursor.execute(sql1)
        # print(sql1)
        timestamp = self.cursor.fetchone()
        if timestamp is not None:
            timestamp = timestamp[0]
            return timestamp
        else:
            return None

    def get_last_price(self, table_name, interval_type, last_ts):
        """
        获取最近的收盘价
        :param table_name:
        :param interval_type:
        :param last_ts: 最近的时间戳
        :return:
        """
        sql1 = f"SELECT close FROM `{table_name}` WHERE interval_type = '{interval_type}'\
         and time_stamp < {last_ts} ORDER BY time_stamp DESC LIMIT 1"
        self.cursor.execute(sql1)
        data = self.cursor.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def query_ohlcv(self, table_name: str, symbol: str, interval_type: str, since_timestamp: int, limit: int):
        """
        获取open(开盘价格)、high(最高价格)、low(最低价格)、close(收盘价格)、volume(交易量)
        :param table_name: 表格名称，也就是交易所名称
        :param symbol: 交易对
        :param interval_type: 间隔类型，目前只支持m15与h1
        :param since_timestamp: 从那个时间戳往前推
        :param limit: 获取的数据长度，默认为100,最大为1000
        """
        sql1 = f"""SELECT time_stamp, open, high, low, close,volume  FROM `{table_name}`  \
        WHERE symbol="{symbol}" AND interval_type="{interval_type}" AND time_stamp <= {since_timestamp}\
        ORDER BY time_stamp DESC LIMIT {limit}"""
        print(sql1)
        self.cursor.execute(sql1)
        data = self.cursor.fetchall()
        if data is not None:
            return sorted(data, key=lambda x: x[0])
        else:
            return None


if __name__ == '__main__':
    my_sql = MySQL()