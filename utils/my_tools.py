import datetime
import time


def interval2timestamp(interval):
    """
    编写一个时间间隔转时间戳的函数
    :param interval: 时间间隔可选择m1, m5, m15, m30, h1, h2, h4, h8, h12, d1, w1
    :return:
    """
    if interval == 'm1':
        stamp = 60
        interval = "1m"
    elif interval == 'm15':
        stamp = 60 * 15
        interval = "15m"
    elif interval == 'm30':
        stamp = 60 * 30
        interval = "30m"
    elif interval == 'h1':
        stamp = 60 * 60
        interval = "1h"
    elif interval == 'h2':
        stamp = 60 * 60 * 2
        interval = "2h"
    elif interval == 'h4':
        stamp = 60 * 60 * 4
        interval = "4h"
    elif interval == 'd1':
        stamp = 60 * 60 * 24
        interval = "1d"
    elif interval == 'w1':
        stamp = 60 * 60 * 24 * 7
        interval = "1w"
    else:
        raise Exception('interval is error')
    return stamp * 1000, interval


def stamp2time(stamp: int):
    """
    时间戳转时间
    :param stamp:
    :return:
    """
    if stamp > 10 ** 12:
        stamp = stamp / 1000
    date_time = datetime.datetime.fromtimestamp(stamp)
    time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return time_str


def time2stamp(time_str: str):
    """
    编写一个简单的时间转时间戳函数
    :param time_str: 时间，建议格式为"%Y-%m-%d %H:%M:S"
    :return:
    """
    if '-' not in time_str:
        raise Exception('You time format may be wrong! You should do like "%Y-%m-%d %H:%M:%S",'
                        ' such as ""2020-01-02 11:00:00')
    time_array = time.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    time_stamp = int(time.mktime(time_array)) * 1000
    return time_stamp
