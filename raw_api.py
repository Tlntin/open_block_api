import requests
from pprint import pprint
from datetime import datetime
import pandas as pd


class RawApi(object):
    """
    用于CoinCap的api相关信息获取
    官方文档：https://docs.coincap.io/?version=latest#aff336c8-9d06-4654-bc15-a56cef06a69e
    """

    def __init__(self):
        pass

    @staticmethod
    def get_exchange():
        """
        获取交易所id,也就是交易所名称
        :return:
        """
        url = "https://api.coincap.io/v2/exchanges"
        payload = {}
        headers = {}
        response = requests.get(url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json().get('data', False)
            data = [da['exchangeId'] for da in data]
            # pprint(data)
            return data

    @staticmethod
    def get_market(exchange_id, limit=200):
        """
        获取市场信息，比如交易对名称，全称等等
        :param exchange_id: 交易所id，也就是交易所名称
        :param limit: 返回的币种信息条数，最大2000条,默认200条
        :return:
        """
        url = "https://api.coincap.io/v2/markets"
        params = {
            'exchangeId': exchange_id,
            'limit': limit
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('data', False)
            if bool(data):
                # pprint(data)
                return data

    def get_candles(self, exchange, interval, base_id, quote_id, start=None, end=None):
        """
        获取K线图
        :return:
        """
        url = 'https://api.coincap.io/v2/candles'
        if start is None or end is None:
            params = {
                'exchange': exchange,
                'interval': interval,
                'baseId': base_id,
                'quoteId': quote_id,
            }
        else:
            params = {
                'exchange': exchange,
                'interval': interval,
                'baseId': base_id,
                'quoteId': quote_id,
                'start': start,
                'end': end
            }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('data', False)
            if bool(data):
                data = self.parse_data(data)
                return data
            else:
                print('该交易所没有你想要的数据，换一个交易所试试吧')

    @staticmethod
    def parse_data(data):
        """
        对K线数据进行简单处理，返回一个DataFrame
        :param data: 原始数据
        :return:
        """
        data1 = [list(da.values()) for da in data]
        data1 = [[float(d) for d in da1] for da1 in data1]
        df = pd.DataFrame(data1, columns=data[0].keys())
        time_list = df.period.apply(lambda x: datetime.fromtimestamp(int(x) / 1000).strftime('%Y-%m-%d %H:%M:%S'))
        df.insert(0, 'time', time_list)
        df.pop('period')
        return df


if __name__ == '__main__':
    api = RawApi()
    e = api.get_exchange()
    pprint(e)
    # df1 = api.get_candles('poloniex', 'h1', 'bitcoin', 'tether', 1514739600000, 1515344400000)
    # print(df1)
    # api.get_market('huobi', 500)