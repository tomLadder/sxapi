#!/usr/bin/python
# coding: utf8

import datetime

def toTS(dt):
    if isinstance(dt, datetime.datetime):
        return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())
    if isinstance(dt, datetime.date):
        return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())
    return int(dt)


def fromTS(ts):
    if isinstance(ts, datetime.datetime):
        return ts
    if isinstance(ts, datetime.date):
        return datetime.datetime.combine(ts, datetime.datetime.min.time())
    return datetime.datetime.utcfromtimestamp(ts)


def splitDateRange(start, end, days):
    assert start <= end
    f = toTS(start)
    t = toTS(end)
    diff = days * 24 * 60 * 60
    last = f
    #left = end - start
    for i in range(f, t - diff, diff):
        last = i+diff-1
        yield (fromTS(i), fromTS(last))
    if last < t:
        yield (fromTS(last+1), fromTS(t))

def splitTimeRange(start, end, days):
    assert start <= end
    f = int(start)
    t = int(end)
    diff = days * 24 * 60 * 60
    last = f
    #left = end - start
    for i in range(f, t - diff, diff):
        last = i+diff-1
        yield (i, last)
    if last < t:
        yield (last+1, t)