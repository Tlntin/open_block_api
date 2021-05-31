import requests
from pprint import pprint
from datetime import datetime
import pandas as pd
from fake_useragent import UserAgent


class RawApi(object):
    """
    用于CoinCap的api相关信息获取
    官方文档：https://docs.coincap.io/?version=latest#aff336c8-9d06-4654-bc15-a56cef06a69e
    """

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
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        response = s.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('data', False)
            if bool(data):
                # pprint(data)
                return data


if __name__ == '__main__':
    api = RawApi()
    e = api.get_exchange()
    pprint(e)