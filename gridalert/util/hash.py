import hashlib

def md5(cluster, host, date, service, data):

    dat = cluster + host + date + service + data
    hs = hs = hashlib.md5(dat.encode()).hexdigest()

    return hs
