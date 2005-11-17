
#
# $Id: utils.py,v 1.2 2005/11/17 13:28:06 lightdruid Exp $
#
# $Log: utils.py,v $
# Revision 1.2  2005/11/17 13:28:06  lightdruid
# Id/Log tags added
#
#

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

