from fastapi import FastAPI
from utils.sql import MySQL
import uvicorn
import time
from fastapi.responses import HTMLResponse


app = FastAPI()


@app.get('/')
async def root():
    content = """
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <title>首页</title>
    </head>
    <body>
        <a href="/docs">查看文档</a>
    </body>
    </html>
    """
    return HTMLResponse(content=content, status_code=200)


@app.get("/ohlcv")
async def fetch_ohlcv(exchange: str, symbol: str, interval: str, since_timestamp: int = None, limit: int = 100):
    """
    获取open(开盘价格)、high(最高价格)、low(最低价格)、close(收盘价格)、volume(交易量)</br>
    :param exchange: 交易所名称</br>
    :param symbol: 交易对</br>
    :param interval: 间隔，目前只支持m15与h1</br>
    :param since_timestamp: 从那个时间戳往前推</br>
    :param limit: 获取的数据长度，默认为100,最大为1000</br>
    """
    limit = min(limit, 1000)
    if since_timestamp is None:
        since_timestamp = int(time.time() * 1000)
    mysql = MySQL()
    data = mysql.query_ohlcv(exchange, symbol, interval, since_timestamp, limit)
    if data is not None:
        return data
    else:
        return False


@app.get("/close_price")
async def close_price(exchange: str, symbol: str, interval: str, since_timestamp: int = None):
    """
    获取最近的收盘价
    :param
    """
    mysql = MySQL()
    if since_timestamp is None:
        since_timestamp = int(time.time() * 1000)
    data = mysql.query_ohlcv(exchange, symbol, interval, since_timestamp, 1)
    if data is not None:
        return data[0][-2]
    else:
        return False

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8080)
    # uvicorn web_api:app --reload
