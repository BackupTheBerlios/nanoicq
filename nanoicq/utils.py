def ashex(data):
    out = ''
    for c in data: 
        out += "%02X" % ord(c)
    return out

def fromhex(data):
    out = ''
    for c in data: 
        out += "%02X" % ord(c)
    return out

