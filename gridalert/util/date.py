import time
import datetime

#from gensim.models.doc2vec import Doc2Vec

def endate_to_unix(date):
    # e.g. Mon Feb 18 04:02:07 2019
    return  time.mktime(datetime.datetime.strptime(date, "%c").timetuple())

def sqdate_to_unix(date):
    # e.g. YYYY-MM-DD HH:MM:SS
    return  time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple())

def unix_to_sqdate(unix):
    # e.g. YYYY-MM-DD HH:MM:SS
    return  datetime.datetime.fromtimestamp(unix)

def endate_to_sqdate(date):
    unix = endate_to_unix(date)
    return unix_to_sqdate(unix)

def in_sqdate(date, start, end):
    date  = sqdate_to_unix(date)
    start = sqdate_to_unix(start)
    end   = sqdate_to_unix(end)
    return (date > start) and (date < end)
