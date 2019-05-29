import hashlib

def md5(data):

    dat = ''.join(data)
    hs = hs = hashlib.md5(dat.encode()).hexdigest()

    return hs
