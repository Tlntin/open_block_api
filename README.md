# 中文说明 | [English](README_en.md)
## 开源免费获取数字货币历史行情信息工具

## 使用说明
1. 在当前文件新建log文件夹，用于储存简单的log日志。
2. 将config_sample.yaml改成config.yaml。
3. 填写config.yaml文件里面的数据库信息，以及决定是否开启代理，多线程。
4. 不建议修改每次获取的数据条数。
5. 根据config.yaml，创建好数据库，默认是API数据库
6. 运行sync.py文件，即可开始同步数据

## 新增Docker容器
- 封装了HT交易所自2019年初到2021年5月初的15min,1h,1d数据(1d不怎么准，不建议用)
1. 打包Docker
```bash
docker build . -t ht_db
```
2. 启动容器-初始化数据
```bash
docker run --name ht_db -p 3307:3306 \
        -e MYSQL_ROOT_PASSWORD=123456 \
        -d ht_db
```
3. 查看启动日志
```bash
docker logs -f ht_db
```
4. 保险起见，去docker容器查看一番
```bash
docker exec -it ht_db /bin/bash
```
### 直接拉取Docker镜像
```bash
# 树莓派
docker pull registry.cn-hangzhou.aliyuncs.com/tlntin/ht_db:arm64
# 普通pc
docker pull registry.cn-hangzhou.aliyuncs.com/tlntin/ht_db
```

## 注意
1. 目前同步时间比较慢，请耐心等待。
2. 暂不考虑为多币种启动多进程，后期可能会考虑。

## 更新记录
#### 2021-06-01更新
1. 使用yaml文件来配置数据库，代理，多线程。
2. 支持多线程，支持数据存储到数据库。
3. 优化数据缺失情况下的数据补全情况
4. 增加web,api,模拟回测环境。
5. 定时同步功能。

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
- 新增加了一个"bitcoin_charts.py"，可以通过[下载](http://api.bitcoincharts.com/v1/csv/)原始的csv数据合成K线数据，该数据同样可以自定义时间间隔。
