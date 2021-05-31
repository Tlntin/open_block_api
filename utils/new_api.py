from my_thread.get_multi_data import GetMultiData
from utils.raw_api import RawApi
import pandas as pd
from utils.my_tools import time2stamp, stamp2time
from utils.sql import MySQL
import os


class NewApi(GetMultiData):
    def __init__(self, exchange: str, interval, symbol, start_ts: int, end_ts: int):
        """
        初始化构造函数
        :param exchange: 交易所名称，比如huobi
        :param interval: 间隔，比如m15,h1, d1
        :param symbol: 交易对名称，比如BTC/USDT
        :param start_ts: 开始时间，int,13位时间戳
        :param end_ts: 结束时间，int, 13位时间戳
        """
        self.symbol = symbol
        self.exchange = exchange
        base_id, quote_id = self.split_symbol()
        # print(base_id, quote_id)
        super().__init__(exchange, interval, base_id, quote_id, start_ts, end_ts)
        # 加入一个时间戳检测，必须填写的时间戳以小时为单位,防止出现异常
        if not start_ts % (1000 * 3600) == 0:
            raise Exception("输入的时间戳必须以小时为单位，不允许出现分钟或者秒")
        if not end_ts % (1000 * 3600) == 0:
            raise Exception("输入的时间戳必须以小时为单位，不允许出现分钟或者秒")

    def split_symbol(self):
        """
        切割交易对，变成两个基础币种
        :return:
        """
        api = RawApi()
        if self.exchange not in api.get_exchange():
            raise Exception('exchange_id may be wrong, please check it')
        symbol = self.symbol.upper()
        if '_' in symbol:
            symbol_list = symbol.split('_')
        elif '/' in symbol:
            symbol_list = symbol.split('/')
        else:
            raise Exception('Symbol写法有误，请参造BTC/USDT这种写法去写')
        # 需要将Symbol格式化为原始api提供的id格式
        base_symbol = symbol_list[0]  # 基础交易币种，比如比特币
        quote_symbol = symbol_list[1]  # 转换结算币种，比如USDT
        market_list = api.get_market(self.exchange, limit=500)
        # 获取基础币种id和结算币种id
        # 先构建一个转换字典
        trans_dict = {}
        for data in market_list:
            trans_dict[data["baseSymbol"]] = data["baseId"]
            trans_dict[data["quoteSymbol"]] = data["quoteId"]
        # base_id = [data['baseId'] for data in market_list if data['baseSymbol'] == base_symbol][0]
        # quote_id = [data['quoteId'] for data in market_list if data['quoteSymbol'] == quote_symbol][0]
        base_id = trans_dict[base_symbol]
        quote_id = trans_dict[quote_symbol]
        return base_id, quote_id

    def process_df(self, temp_df: pd.DataFrame):
        """
        处理一下DataFrame，让他格式兼容数据库
        :param temp_df:
        :return:
        """
        temp_df.insert(0, 'interval_type', self.new_interval)
        temp_df.insert(0, 'symbol', self.symbol)
        # print(temp_df.columns)
        # print(temp_df)
        time_stamp = temp_df['time'].apply(time2stamp)
        temp_df.insert(3, 'time_stamp', time_stamp)
        data = temp_df.values.tolist()
        return data

    def fill_df(self, temp_df: pd.DataFrame, start_ts: int, end_ts: int):
        """
        用于填充数量不够的DataFrame
        :param temp_df: 需要填充的DataFrame
        :param start_ts: 开始时间戳
        :param end_ts: 结束时间戳
        """
        temp_df['time_stamp'] = temp_df['time'].apply(time2stamp)
        time_stamp_list = temp_df.time_stamp.values.tolist()
        result_value = []
        start_value = temp_df.loc[0, temp_df.columns[:-1]].values.tolist()  # 定一个初始化值
        for stamp in range(start_ts, end_ts, self.ts_interval):
            if stamp in time_stamp_list:
                start_value = temp_df.loc[temp_df.time_stamp == stamp, temp_df.columns[:-1]].values.tolist()[0]
                value = start_value
            else:
                value = [stamp2time(stamp)]
                value.extend([start_value[-2]] * 4)  # 4代表ohlc都是上个的收盘价格
                value.append(0)
            result_value.append(value)
        df2 = pd.DataFrame(result_value, columns=temp_df.columns[:-1])
        return df2

    def new_get_once_data(self, start_ts, end_ts):
        """
        重构获取单条数据
        :param start_ts:
        :param end_ts:
        :return:
        """
        mysql = MySQL()
        df = self.get_once_data(start_ts, end_ts)
        should_num = (end_ts - start_ts) / self.ts_interval
        if df is not None:
            if isinstance(df, pd.DataFrame):
                # print("中间短点", len(df), should_num)
                if len(df) < should_num:
                    # 需要填充数据
                    # print(f"需要填充一波，填充前有{len(df)}条")
                    df = self.fill_df(df, start_ts, end_ts)
                    # print(f"填充后有{len(df)}条")
                else:
                    pass
            else:
                return "error"  # 返回错误，告诉主线程所有线程都要停下
        else:
            last_price = mysql.get_last_price(self.symbol, self.new_interval, start_ts)
            mysql.cursor.close()
            mysql.db.close()
            # print("当前最近价格：", last_price)
            file_name = "{}log.txt".format(self.symbol.replace("/", "_"))
            log_path = os.path.join(self.parent_dir, self.yaml_dict["log_dir"], file_name)
            if not os.path.exists(log_path):
                f = open(log_path, "wt", encoding="utf-8")
            else:
                f = open(log_path, "at", encoding="utf-8")
            if last_price is not None:
                value_list = []
                for stamp in range(start_ts, end_ts, self.ts_interval):
                    value = [stamp2time(stamp)]
                    value.extend([last_price] * 4)  # 4代表ohlc都是上个的收盘价格
                    value.append(0)
                    value_list.append(value)
                # print(value_list)
                df = pd.DataFrame(value_list, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                f.write('warning 本次没有获取到数据\n')
                f.write('开始生成数据，{}交易对,{}间隔;开始时间{}结束时间{}\n；\t'.\
                        format(self.symbol, self.interval, start_ts, end_ts))
                f.write("\n\n")
            else:
                f.write("error, 本次没有数据，且没有历史数据\n")
                f.write('{}交易对,{}间隔;开始时间{}结束时间{}\n；\t'.\
                        format(self.symbol, self.interval, start_ts, end_ts))
                f.write("\n\n")
                f.close()
                df = None
        return df  # 返回结果，方便前段统计

    def get_temp_multi_df(self, start_index, time_list, func):
        """
        重写临时df获取函数，加入数据库储存
        :param start_index:
        :param time_list:
        :param func: 多线程执行的函数，因为要发生重写，所以这里最好用一个变量执行比较好
        :return:
        """
        df, total_num = super().get_temp_multi_df(start_index, time_list, func)
        # 然后储存到数据库
        mysql = MySQL()
        data = self.process_df(df)
        mysql.insert_table(self.symbol, data)
        mysql.cursor.close()
        mysql.db.close()
        return df, total_num

    def run(self):
        time_list = self.get_time_list()
        result_df = self.get_multi_data(time_list, func=self.new_get_once_data)  # 换上新函数，可以补全
        return result_df


if __name__ == '__main__':
    # api = NewApi('huobi', 'm15', "BTC/USDT", 1570813200000, 1570986000000)
    # 1549011028000
    api = NewApi('huobi', 'm15', "BTC/USDT", 1550390400000, 1552424400000)
    result_df1 = api.run()
    print(result_df1)
