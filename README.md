## 开源免费获取数字货币历史行情信息工具

## 主要功能

- 根据不同的交易所，时间间隔，交易币种，获取历史K线信息，便于搭建量化模拟盘
- 数据来源：[CoinCap](https://docs.coincap.io/?version=latest#51da64d7-b83b-4fac-824f-3f06b6c8d944)

## 其它说明

- 支持的交易所，共有73个，具体如下：

```shell
['binance',
 'huobi',
 'coinbene',
 'bibox',
 'hitbtc',
 'bit-z',
 'gdax',
 'coinex',
 'zb',
 'kucoin',
 'kraken',
 'bitmax',
 'lbank',
 'qryptos',
 'quoine',
 'bitfinex',
 'hotbit',
 'gate',
 'bitstamp',
 'yobit',
 'coinone',
 'bitflyer',
 'bittrex',
 'livecoin',
 'bilaxy',
 'poloniex',
 'exmo',
 'mercatox',
 'bitbank',
 'bitbay',
 'zaif',
 'gemini',
 'btcbox',
 'lakebtc',
 'independentreserve',
 'tidex',
 'cex',
 'luno',
 'bitso',
 'korbit',
 'btcmarket',
 'itbit',
 'idex',
 'coinfloor',
 'xbtce',
 'therocktrading',
 'kuna',
 'mercado',
 'lykke',
 'coinmate',
 'btctradeua',
 'braziliex',
 'bleutrade',
 'bigone',
 'ooobtc',
 'acx',
 'bithumb',
 'okex',
 'okcoin',
 'bxinth',
 'tradesatoshi',
 'allcoin',
 'btcturk',
 'gatecoin',
 'sistemkoin',
 'cryptopia',
 'coinegg',
 'raisex',
 'bitmarket',
 'coinnest',
 'ccex',
 'coinexchange',
 'btcc']
```

- 支持的时间间隔

```shell
m1, m5, m15, m30, h1, h2, h4, h8, h12, d1, w1
```

- 支持的时间范围，具体视交易所而定，大部分交易所支持2018年之前的K线数据，少部分支持2015年之前的K线数据

## 使用方法

- 可以参考new_api.py文件

## 其它获取比特币历史数据的方式

- 参考notebook文件，这个bittrex交易所可以获取到2015年之前的数据，不过有的没有交易量
- 如果要逐笔订单，可以看看这个http://api.bitcoincharts.com/v1/csv/
- 新增加了一个"bittrex.py"，可以一键获取bittrex交易所的历史K线数据
