import hashlib

def md5(cluster, host, date, data):

    dat = cluster + host + date + data
    hs = hs = hashlib.md5(dat.encode()).hexdigest()

    return hs
