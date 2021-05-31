## Open source and free access to digital currency historical market information tool

## Instructions for use
1. Create a log folder in the current file to store simple log logs.
2. Change config_sample.yaml to config.yaml.
3. Fill in the database information in the config.yaml file, and decide whether to open the proxy, multithreading.
4. It is not recommended to modify the number of data obtained each time.
5. According to config.yaml, create a database, the default is API database
6. Run the sync.py file to start synchronizing data

## Note
1. The current synchronization time is relatively slow, please be patient.
2. For the time being, we will not consider launching multiple processes for multiple currencies, it may be considered later.

## update record
#### Update 2021-06-01
1. Use yaml files to configure database, proxy, and multithreading.
2. Supports multi-threading and data storage to the database.
3. Optimize the data completion situation in the case of missing data
4. Add web and api to simulate the backtest environment.
5. Timing synchronization function.

## The main function

-Obtain historical K-line information according to different exchanges, time intervals, and trading currencies, which is convenient for building quantitative simulation disks
-Data source: [CoinCap](https://docs.coincap.io/?version=latest#51da64d7-b83b-4fac-824f-3f06b6c8d944)

## other instructions

-There are 73 exchanges supported, as follows:

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

-Supported time interval

```shell
m1, m5, m15, m30, h1, h2, h4, h8, h12, d1, w1
```

-The supported time range depends on the exchange. Most exchanges support K-line data before 2018, and a small part support K-line data before 2015

## Instructions

-You can refer to the new_api.py file

## Other ways to get historical Bitcoin data

-Refer to the notebook file, this bittrex exchange can get data before 2015, but some have no transaction volume
-If you want to order one by one, you can take a look at this http://api.bitcoincharts.com/v1/csv/
-A new "bittrex.py" has been added, which can obtain historical K-line data of bittrex exchange with one click
-A new "bitcoin_charts.py" has been added, which can be used to synthesize K-line data with [download](http://api.bitcoincharts.com/v1/csv/) original csv data, and the data can also be customized with a time interval.
