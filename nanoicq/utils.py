
#
# $Id: utils.py,v 1.3 2005/12/13 15:25:47 lightdruid Exp $
#
# $Log: utils.py,v $
# Revision 1.3  2005/12/13 15:25:47  lightdruid
# Trying to figure out why SNAC 13,4 doesn't work
#
# Revision 1.2  2005/11/17 13:28:06  lightdruid
# Id/Log tags added
#
#

import string

def ashex(data, sep = ''):
    out = ''
    for c in data: 
        out += ("%02X" + sep) % ord(c)
    return out

def fromhex(data):
    out = ''
    for c in data: 
        out += "%02X" % ord(c)
    return out

def asdump(s):
    out = ''
    for c in s: 
        if c not in string.printable: c = '.'
        if c in '\t\n\r\v\f': c = '.'
        out += c
    return out

def coldump(s):
    out = ''
    while s:
        out += "%-48s" % ashex(s[:16], ' ') + "%-16s" % asdump(s[:16]) + '\n'
        s = s[16:]
    return out

# ---
