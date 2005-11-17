
#
# $Id: isocket.py,v 1.2 2005/11/17 13:28:06 lightdruid Exp $
#
# $Log: isocket.py,v $
# Revision 1.2  2005/11/17 13:28:06  lightdruid
# Id/Log tags added
#
#

import sys
import time
import struct
import socket
from utils import *
from snacs import *

import caps

def _reg(password):
    lz = struct.pack(">H", len(password)) + password + '\000'
    print len(lz)
    return "\0x00\0x00\0x00\0x00\0x28\0x00\0x03\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x9e\0x27\0x00\0x00\0x9e\0x27\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00" + lz + "\0x9e\0x27\0x00\0x00\0x00\0x00\0x00\0x00\0x03\0x02"


_userClasses = {
0x0001: "CLASS_UNCONFIRMED",
0x0002: "CLASS_ADMINISTRATOR",
0x0004: "CLASS_AOL",
0x0008: "CLASS_COMMERCIAL",
0x0010: "CLASS_FREE",
0x0020: "CLASS_AWAY",
0x0040: "CLASS_ICQ",
0x0080: "CLASS_WIRELESS",
0x0100: "CLASS_UNKNOWN100",
0x0200: "CLASS_UNKNOWN200",
0x0400: "CLASS_UNKNOWN400",
0x0800: "CLASS_UNKNOWN800",
}

_messageTypes = {
0x01:    "MTYPE_PLAIN",
0x02:    "MTYPE_CHAT",
0x03:    "MTYPE_FILEREQ",
0x04:    "MTYPE_URL",
0x06:    "MTYPE_AUTHREQ",
0x07:    "MTYPE_AUTHDENY",
0x08:    "MTYPE_AUTHOK",
0x09:    "MTYPE_SERVER",
0x0C:    "MTYPE_ADDED",
0x0D:    "MTYPE_WWP",
0x0E:    "MTYPE_EEXPRESS",
0x13:    "MTYPE_CONTACTS",
0x1A:    "MTYPE_PLUGIN",
0xE8:    "MTYPE_AUTOAWAY",
0xE9:    "MTYPE_AUTOBUSY",
0xEA:    "MTYPE_AUTONA",
0xEB:    "MTYPE_AUTODND",
0xEC:    "MTYPE_AUTOFFC",
}   

_messageFlags = {
0x01:    "MFLAG_NORMAL",
0x03:    "MFLAG_AUTO",
0x80:    "MFLG_MULTI",
}
    
username = '264025324'
#username = '223606200'

class Log:
    def log(self, msg):
        print "LOG:", msg

    def packetin(self, msg):
        self.log("<- " + ashex(msg))

    def packetout(self, msg):
        self.log("-> " + ashex(msg))

log = Log()

TLV_ErrorURL = 0x0004
TLV_Redirect = 0x0005
TLV_Cookie = 0x0006
TLV_ErrorCode = 0x0008
TLV_DisconnectReason = 0x0009
TLV_DisconnectMessage = 0x000b
TLV_Unknown3 = 0x000c
TLV_EmailAddress = 0x0011
TLV_RegStatus = 0x0013

error_codes = {
0x0001:      "Invalid nick or password"                                                    ,
0x0002:      "Service temporarily unavailable"                                             ,
0x0003:      "All other errors"                                                            ,
0x0004:      "Incorrect nick or password, re-enter"                                        ,
0x0005:      "Mismatch nick or password, re-enter"                                         ,
0x0006:      "Internal client error (bad input to authorizer)"                             ,
0x0007:      "Invalid account"                                                             ,
0x0008:      "Deleted account"                                                             ,
0x0009:      "Expired account"                                                             ,
0x000A:      "No access to database"                                                       ,
0x000B:      "No access to resolver"                                                       ,
0x000C:      "Invalid database fields"                                                     ,
0x000D:      "Bad database status"                                                         ,
0x000E:      "Bad resolver status"                                                         ,
0x000F:      "Internal error"                                                              ,
0x0010:      "Service temporarily offline"                                                 ,
0x0011:      "Suspended account"                                                           ,
0x0012:      "DB send error"                                                               ,
0x0013:      "DB link error"                                                               ,
0x0014:      "Reservation map error"                                                       ,
0x0015:      "Reservation link error"                                                      ,
0x0016:      "The users num connected from this IP has reached the maximum"                ,
0x0017:      "The users num connected from this IP has reached the maximum (reservation)"  ,  
0x0018:      "Rate limit exceeded (reservation). Please try to reconnect in a few minutes" ,  
0x0019:      "User too heavily warned"                                                     ,
0x001A:      "Reservation timeout"                                                         ,
0x001B:      "You are using an older version of ICQ. Upgrade required"                     ,
0x001C:      "You are using an older version of ICQ. Upgrade recommended"                  ,
0x001D:      "Rate limit exceeded. Please try to reconnect in a few minutes"               ,
0x001E:      "Can't register on the ICQ network. Reconnect in a few minutes"               ,
0x0020:      "Invalid SecurID"                                                             ,
0x0022:      "Account suspended because of your age (age < 13)"                            ,
}

def explainError(code):
    return error_codes[struct.unpack("!H", code)[0]]

def encryptPasswordICQ(password):
    key=[0xF3,0x26,0x81,0xC4,0x39,0x86,0xDB,0x92,0x71,0xA3,0xB9,0xE6,0x53,0x7A,0x95,0x7C]
    bytes=map(ord,password)
    r=""
    for i in range(len(bytes)):
        r=r+chr(bytes[i]^key[i%len(key)])
    return r


def tlv(typ, val):
    return struct.pack("!HH", typ, len(val)) + str(val)

def detlv(data):
    return struct.unpack("!HH", data[:4])

def readTLVs(data):
    d = {}
    while data:
        head = detlv(data)
        d[head[0]] = data[4 : 4 + head[1]]
        data = data[4 + head[1]:]
    return d


class ISocket:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._sock.connect((self._host, self._port))

    def disconnect(self):
        if self._sock:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock = None

    def send(self, data):
        self._sock.send(data)

    def read(self, bufsize):
        return self._sock.recv(bufsize)

#2a020d57002a 0001001700000000001700010003000200010003000100150001000400010006000100090001000a0001
#2A0200010036 0001001700000000000000010003000200010003000100040001000600010008000100090001000A0001000B0001000C000100130003
#             00010017000000000000

class Protocol:
    def __init__(self, sock):
        self._sock = sock
        self.buf = ''
        self.statusindicators = 0x0000

    def send(self, data):
        self._sock.send(data)

    def read(self):
        return self._sock.read(1024)

    def sendFLAP(self, ch, data):
        header = "!cBHH"
        if (not hasattr(self, "seqnum")):
            self.seqnum = 0
        self.seqnum = (self.seqnum+1)%0xFFFF
        head = struct.pack(header,'*', ch, self.seqnum, len(data))

        data = head + str(data)
        log.packetout(data)
        self.send(data)

    def readFLAP(self, buf):
        header = "!cBHH"
        if len(buf) < 6: return
        flap = struct.unpack(header, buf[:6])
        if len(buf) < 6 + flap[3]: return
        data, buf = buf[6:6 + flap[3]], buf[6 + flap[3]:]
        return [flap[1], buf, data]

    def encodeSNAC(self, family, subfamily, id, data):
        return struct.pack("!HHBBL", family, subfamily, 0, 0, id) + data

    def sendSNAC(self, family, subfamily, id, data):
        self.sendFLAP(0x02, self.encodeSNAC(family, subfamily, id, data))

    def readSNAC(self, data):
        return list(struct.unpack("!HHBBL", data[:10])) + [data[10:]]

    def sendAuth(self):
        # 264025324
        self.username = username
        encpass = encryptPasswordICQ('zuppa197')

        self.sendFLAP(0x01, '\000\000\000\001'+
            tlv(0x01,self.username)+
            tlv(0x02,encpass)+
            tlv(0x03,'ICQ Inc. - Product of ICQ (TM).2001b.5.18.1.3659.85')+
            tlv(0x16,"\x01\x0a")+
            tlv(0x17,"\x00\x05")+
            tlv(0x18,"\x00\x12")+
            tlv(0x19,"\000\001")+
            tlv(0x1a,"\x0eK")+
            tlv(0x14,"\x00\x00\x00U")+
            tlv(0x0f,"en")+
            tlv(0x0e,"us"))

    def dispatch(self, ch):
        sfunc = "proc_%d_0_0" % ch

#        snac = self.readSNAC(data[1])
#        print snac

        if ch not in [1, 4]:
            func = getattr(self, "proc_%s" % data, None)
        else:
            func = getattr(self, sfunc, None)
        func("data")

    def parseFamilies(self, data):
        self.serverFamilies = []

        while data:
            self.serverFamilies.append(struct.unpack("!H", data[:2])[0])
            data = data[2:]

    def proc_2_1_3(self, data):
        self.parseFamilies(data)
        self.families = supported

        out = ''
        for f in self.serverFamilies:
            if self.families.has_key(f):
                out += struct.pack("!2H", f, self.families[f])

        self.sendSNAC(0x01, 0x17, 0, out)

    def proc_2_1_24(self, data):
        self.sendSNAC(0x01, 0x06, 0, '')

    def proc_2_1_7(self, data):
        ''' Rate info '''

        log.packetin(data)

        count = struct.unpack('!H', data[0:2])[0]
        log.log('Received %d rate groups' % count)

        self.outRateInfo = {}
        self.outRateTable = {}
        resp = ''

        dt = data[2:]
        for ii in range(count):
            info = struct.unpack('!HLLLLLLLLB', dt[:35])

            self.outRateInfo[info[0]] = {
                'window_size'       : info[1],
                'clear_level'       : info[2],
                'alert_level'       : info[3],
                'limit_level'       : info[4],
                'disconnect_level'  : info[5],
                'current_rate'      : info[6],
                'max_level'         : info[7],
                'last_time'         : info[8],
                'current_state'     : info[9],
                }
            log.log("Class ID: " + str(info))
            dt = dt[35:]

        for ii in range(count):
            rgd, npair = struct.unpack('!HH', dt[:4])
            log.log("For family %d server has %d pairs" % (rgd, npair))

            # We want to send it back to server
            resp += struct.pack('!H', rgd)

            dt = dt[4:]
            for jj in range(npair):
                family, subfamily = struct.unpack('!HH', dt[4:8])
                self.outRateTable[family] = subfamily
                dt = dt[4:]

        log.log("Sending connection rate limits")
        self.sendSNAC(0x01, 0x08, 0, resp)

        time.sleep(1)
        log.log("Sending location rights limits")
        self.sendSNAC(0x02, 0x02, 0, '') # location rights info

    def proc_2_9_3(self, data):
        ''' BOS rights '''
        tlvs = readTLVs(data)
        self.maxPermitList = struct.unpack("!H", tlvs[1])[0]
        self.maxDenyList = struct.unpack("!H", tlvs[2])[0]
        log.log("Max permit list: %d, Max deny list: %d" % (self.maxPermitList, self.maxDenyList))

        time.sleep(1)
        log.log("Sending SSI rights info")
        self.sendSNAC(0x13, 0x02, 0, '')

    def proc_2_4_5(self, data):
        ''' ICBM parameters '''
        log.log("Sending changed default ICBM parameters command")
        self.sendSNAC(0x04, 0x02, 0, '\x00\x00\x00\x00\x00\x0b\x1f@\x03\xe7\x03\xe7\x00\x00\x00\x00')

        time.sleep(1)
        log.log("Sending PRM service limitations")
        self.sendSNAC(0x09, 0x02, 0, '')

    def proc_2_3_3(self, data):
        ''' Buddy list rights '''
        tlvs = readTLVs(data)
        self.maxBuddies = struct.unpack("!H", tlvs[1])[0]
        self.maxWatchers = struct.unpack("!H", tlvs[2])[0]
        log.log("Max buddies: %d, Max watchers: %d" % (self.maxBuddies, self.maxWatchers))

        log.log("Sending ICBM service parameters")
        self.sendSNAC(0x04,0x04,0,'') # ICBM parms

    def proc_2_19_3(self, data):
        ''' List service granted, request roster from server '''
        self.sendSNAC(0x13, 0x07, 0, '')

        icqStatus = 0x00
        self.sendSNAC(0x01, 0x1e, 0, tlv(0x06, struct.pack(">HH", self.statusindicators, icqStatus)))

        sf = {
            0x01:(3, 0x0110, 0x059b),
            0x13:(3, 0x0110, 0x059b),
            0x02:(1, 0x0110, 0x059b),
            0x03:(1, 0x0110, 0x059b),
            0x04:(1, 0x0110, 0x059b),
            0x06:(1, 0x0110, 0x059b),
            0x08:(1, 0x0104, 0x0001),
            0x09:(1, 0x0110, 0x059b),
            0x0a:(1, 0x0110, 0x059b),
            0x0b:(1, 0x0104, 0x0001),
            0x0c:(1, 0x0104, 0x0001)
        }

        d = ''
        for fam in self.serverFamilies:
            if sf.has_key(fam):
                print sf[fam]
                version, toolID, toolVersion = sf[fam]
                d = d + struct.pack('!4H', fam, version, toolID, toolVersion)
        self.sendSNAC(0x01, 0x02, 0, d)

    def proc_2_1_15(self, data):
        ''' My status '''

        uinLen = int(struct.unpack('!B', data[0])[0])
        uin = str(data[1 : uinLen + 1])
        print uin

        warningLevel, tlvNumber = struct.unpack('!HH', data[uinLen + 1: uinLen + 1 + 4])
        print warningLevel, tlvNumber

        tlvs = readTLVs(data[uinLen + 1 + 4:])
        self.parseSelfStatus(tlvs)

        log.log("Retrieving server-side contact list")
        self.sendSNAC(0x13, 0x04, 0, '')
#        self.getOfflineMessages()
#        self.sendSNAC(0x13, 0x05, 0, struct.pack('!LH', 0, 0))

    def proc_2_19_6(self, data):
        ''' This is the server reply to client roster 
        requests: SNAC(13,04), SNAC(13,05).

        Server can split up the roster in several parts. This is 
        indicated with SNAC flags bit 1 as usual, however the "SSI 
        list last change time" only exists in the last packet. 
        And the "Number of items" field indicates the number of 
        items in the current packet, not the entire list. '''

        ver = int(struct.unpack('!B', data[0])[0])
        assert ver == 0
        print ashex(data)

        nitems = int(struct.unpack('!H', data[1:3])[0])
        log.log("Items number: %d" % nitems)
        print data[3:]

    def proc_2_19_15(self, data):
        raise Exception("proc_2_19_15 not implemented")

    def parseSelfStatus(self, data):
        self.userClass = int(struct.unpack('!H', data[1])[0])
        self.parseUserClass()

    def parseUserClass(self, userClass = None):
        if userClass is None:
            userClass = self.userClass
        out = []
        for c in _userClasses:
            if userClass & c: out.append(_userClasses[c])
        log.log("User class: " + ' '.join(out))

    def proc_2_4_7(self, data):
        ''' Message received '''
        cookie = data[0:7]
        messageChannel = int(struct.unpack('!H', data[8:10])[0])
        snameLen = int(struct.unpack('!B', data[10])[0])
        sname = data[11:11 + snameLen]
        data = data[11 + snameLen:]

        log.log('Got message, channel: %d, from: %s' % 
            (messageChannel, sname))

        senderWarningLevel = int(struct.unpack('!H', data[0:2])[0])
        tlvNumber = int(struct.unpack('!H', data[2:4])[0])

        tlvs = readTLVs(data[4:])

        userClass = int(struct.unpack('!H', tlvs[1])[0])
        try:
            userStatus = int(struct.unpack('!L', tlvs[6])[0])
        except KeyError, msg:
            log.log("Unable to fetch user status")
        accCreationTime = int(struct.unpack('!L', tlvs[3])[0])
        clientIdleTime = int(struct.unpack('!L', tlvs[0x0f])[0])

        # Dispatch on message channel
        tmp = "proc_2_4_7_%d" % messageChannel
        func = getattr(self, tmp)
        func(tlvs)

    # 13 1C / 19 28

    def proc_2_19_28(self, data):
        ''' you-were-added" message '''
        data = data[8:]
        ln = int(struct.unpack('!B', data[0])[0])
        uin = str(data[1:])
        log.log("You-were-added from " + uin)

    def parseMessageType(self, mtype):
        out = []
        for t in _messageTypes:
            if t & mtype: out.append(_messageTypes[t])
        log.log("Message type: " + " ".join(out))

    def parseMessageFlags(self, mflags):
        out = []
        for t in _messageFlags:
            if t & mflags: out.append(_messageFlags[t])
        log.log("Message flags: " + " ".join(out))

    def proc_2_4_7_4(self, tlvs):
        '''  Channel 4 message format (plain-text messages) '''
        t = tlvs[0x05]
        uin = int(struct.unpack('<L', t[0:4])[0])
        mtype = int(struct.unpack('!B', t[4:5])[0])
        mflags = int(struct.unpack('!B', t[5:6])[0])
        ln = int(struct.unpack('<H', t[6:8])[0])
        msg = t[8:]

        log.log("Message type 4, UIN: %d, length: %d, contents: %s"
            % (uin, ln, str(msg)))

        self.parseMessageType(mtype)
        self.parseMessageFlags(mflags)

    def proc_2_4_7_1(self, tlvs):
        '''  Channel 1 message format (typed old-style messages) '''
        t = tlvs[0x02]
        ln = int(struct.unpack('!H', t[2:4])[0])

        t = t[4 + ln + 2:]
        ln = int(struct.unpack('!H', t[0:2])[0])
        charset = int(struct.unpack('!H', t[2:4])[0])
        sub_charset = int(struct.unpack('!H', t[4:6])[0])
        msg = t[6:]

        log.log('Message type 1: ' + str(msg))

    def proc_2_2_3(self, data):
        ''' Client service parameters request '''
        tlvs = readTLVs(data)
        self.maxProfileLength = struct.unpack('!H', tlvs[1])[0]
        self.maxCapabilities = struct.unpack('!H', tlvs[2])[0]
        log.log("MaxProfileLength: %d, MaxCapabilities: %d" %
            (self.maxProfileLength, self.maxCapabilities))

        self.capabilities = [caps.ICQ, caps.RELAY, caps.UTF8]

        tlvs = tlv(5, ''.join(self.capabilities))

        log.log("Sending client capabilities")
        self.sendSNAC(0x02, 0x04, 0, tlvs)

        # Client use this SNAC to request buddylist service parameters 
        # and limitations. Server should reply via SNAC(03,03).

        time.sleep(0.1)
        log.log("Sending buddylist service parameters ")
        self.sendSNAC(0x03, 0x02, 0, '')

    def proc_1_0_0(self, data):
        print "Logging in..."

    def CLI_FIND_BY_UIN2(self):
        log.log("CLI_FIND_BY_UIN2")
        tlvs = tlv(0x01, struct.pack())

    def CLI_WHITE_PAGES_SEARCH2(self):
        log.log("CLI_WHITE_PAGES_SEARCH2")


    def getOfflineMessages(self):
        ''' Client sends this SNAC when wants to retrieve messages 
        that was sent by another user and buffered by server during 
        client was offline. '''

        tlvs = tlv(0x01, '\x00\x08' + struct.pack("<L", int(username)) + '\x3c\x00\x02\x00')
        self.sendSNAC(0x15, 0x02, 0, tlvs)
        pass


def _test():

    s = ISocket('login.icq.com', 5190)
    s.connect()

    p = Protocol(s)
    buf = p.read()
    log.packetin(buf)

    p.sendAuth()
    buf = p.read()
    log.packetin(buf)

    snac = p.readSNAC(buf)
    i=snac[5].find("\000")
    snac[5]=snac[5][i:]
    tlvs=readTLVs(snac[5])
    log.log(tlvs)

    if tlvs.has_key(TLV_ErrorCode):
        log.log("Error: " + explainError(tlvs[TLV_ErrorCode]))

    server = ''
    if tlvs.has_key(TLV_Redirect):
        server = tlvs[TLV_Redirect]
        log.log("Redirecting to: " + server)

    s.disconnect()
    host, port = server.split(':')

    # ===============
    s = ISocket(host, int(port))
    s.connect()
    p = Protocol(s)

    # ================================
    buf = p.read()
    log.packetin(buf)

    p.sendFLAP(0x01, '\000\000\000\001' + tlv(0x06, tlvs[TLV_Cookie]))

    # ================================

    while 1:
        buf = p.read()
        log.packetin(buf)

        ch, b, c = p.readFLAP(buf)
        snac = p.readSNAC(c)
#        print snac
        print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])

        tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
        func = getattr(p, tmp)

        func(snac[5])

if __name__ == '__main__':
    _test()


        