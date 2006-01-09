#!/bin/env python2.4

#
# $Id: icq.py,v 1.19 2006/01/09 15:08:34 lightdruid Exp $
#

#username = '264025324'
username = '223606200'
#username = '177033621'

import sys
import os
import time
import struct
import socket
import types

from utils import *
from snacs import *
from isocket import ISocket

from buddy import Buddy
from group import Group

import caps
from logger import log, LogException

# for debug only
SLEEP = 0

def _reg(password):
    lz = struct.pack(">H", len(password)) + password + '\000'
    return "\0x00\0x00\0x00\0x00\0x28\0x00\0x03\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x9e\0x27\0x00\0x00\0x9e\0x27\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00" + lz + "\0x9e\0x27\0x00\0x00\0x00\0x00\0x00\0x00\0x03\0x02"

_directConnectionType = {
0x0000: "DC_DISABLED",       # Direct connection disabled / auth required    
0x0001: "DC_HTTPS",          # Direct connection thru firewall or https proxy    
0x0002: "DC_SOCKS",          # Direct connection thru socks4/5 proxy server  
0x0004: "DC_NORMAL",         # Normal direct connection (without proxy/firewall) 
0x0006: "DC_WEB",            # Web client - no direct connection
}

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

_userStatusP1 = {
  0x0001:      "STATUS_WEBAWARE", #     Status webaware flag  
  0x0002:      "STATUS_SHOWIP", #       Status show ip flag   
  0x0008:      "STATUS_BIRTHDAY", #     User birthday flag    
  0x0020:      "STATUS_WEBFRONT", #     User active webfront flag 
  0x0100:      "STATUS_DCDISABLED", #       Direct connection not supported   
  0x1000:      "STATUS_DCAUTH", #       Direct connection upon authorization  
  0x2000:      "STATUS_DCCONT", #       DC only with contact users    
}

_userStatusP2 = {
  0x0000:      "STATUS_ONLINE", #       Status is online  
  0x0001:      "STATUS_AWAY", #     Status is away    
  0x0002:      "STATUS_DND", #      Status is no not disturb (DND)    
  0x0004:      "STATUS_NA", #       Status is not available (N/A) 
  0x0010:      "STATUS_OCCUPIED", #     Status is occupied (BISY) 
  0x0020:      "STATUS_FREE4CHAT", #        Status is free for chat   
  0x0100:      "STATUS_INVISIBLE", #        Status is invisible
}

SSI_ITEM_BUDDY      = 0x0000  # Buddy record (name: uin for ICQ and screenname for AIM)
SSI_ITEM_GROUP      = 0x0001  # Group record
SSI_ITEM_PERMIT     = 0x0002  # Permit record ("Allow" list in AIM, and "Visible" list in ICQ)
SSI_ITEM_DENY       = 0x0003  # Deny record ("Block" list in AIM, and "Invisible" list in ICQ)
SSI_ITEM_VISIBILITY = 0x0004  # Permit/deny settings or/and bitmask of the AIM classes
SSI_ITEM_PRESENCE   = 0x0005  # Presence info (if others can see your idle status, etc)
SSI_ITEM_UNKNOWN1   = 0x0009  # Unknown. ICQ2k shortcut bar items ?
SSI_ITEM_IGNORE     = 0x000e  # Ignore list record.
SSI_ITEM_NONICQ     = 0x0010  # Non-ICQ contact (to send SMS). Name: 1#EXT, 2#EXT, etc
SSI_ITEM_UNKNOWN2   = 0x0011  # Unknown.
SSI_ITEM_IMPORT     = 0x0013  # Item that contain roaster import time (name: "Import time")
SSI_ITEM_BUDDYICON  = 0x0014  # Buddy icon info. (names: from "0" and incrementing by one)

_SSIItemTypes = {
0x0000 : 'SSI_ITEM_BUDDY',
0x0001 : 'SSI_ITEM_GROUP',     
0x0002 : 'SSI_ITEM_PERMIT',    
0x0003 : 'SSI_ITEM_DENY',      
0x0004 : 'SSI_ITEM_VISIBILITY',
0x0005 : 'SSI_ITEM_PRESENCE',  
0x0009 : 'SSI_ITEM_UNKNOWN1',  
0x000e : 'SSI_ITEM_IGNORE',    
0x0010 : 'SSI_ITEM_NONICQ',    
0x0011 : 'SSI_ITEM_UNKNOWN2',  
0x0013 : 'SSI_ITEM_IMPORT',    
0x0014 : 'SSI_ITEM_BUDDYICON',
} 

_reasons = {
0 : "Message was invalid",
1 : "Message was too large",
2 : "Message rate exceeded",
3 : "Sender too evil (sender warn level > your max_msg_sevil)",
4 : "You are too evil (sender max_msg_revil > your warn level)",
}

def explainReason(r):
    return _reasons[r]
        

def explainSSIItemType(t):
    out = ''
    for flag in _SSIItemTypes:
        if t == flag: 
            out = _SSIItemTypes[flag]
            break
    return out

TLV_ErrorURL = 0x0004
TLV_Redirect = 0x0005
TLV_Cookie = 0x0006
TLV_ErrorCode = 0x0008
TLV_DisconnectReason = 0x0009
TLV_DisconnectMessage = 0x000b
TLV_Unknown3 = 0x000c
TLV_EmailAddress = 0x0011
TLV_RegStatus = 0x0013

_error_codes = {
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

_msg_error_codes = {
0x01:    "Invalid SNAC header",
0x02:    "Server rate limit exceeded",    
0x03:    "Client rate limit exceeded",    
0x04:    "Recipient is not logged in",    
0x05:    "Requested service unavailable", 
0x06:    "Requested service not defined", 
0x07:    "You sent obsolete SNAC",    
0x08:    "Not supported by server",   
0x09:    "Not supported by client",   
0x0A:    "Refused by client", 
0x0B:    "Reply too big", 
0x0C:    "Responses lost",    
0x0D:    "Request denied",    
0x0E:    "Incorrect SNAC format", 
0x0F:    "Insufficient rights",   
0x10:    "In local permit/deny (recipient blocked)",  
0x11:    "Sender too evil",   
0x12:    "Receiver too evil", 
0x13:    "User temporarily unavailable",  
0x14:    "No match",  
0x15:    "List overflow", 
0x16:    "Request ambiguous", 
0x17:    "Server queue full", 
0x18:    "Not while on AOL",
}        
    
def explainError(code):
    return _error_codes[struct.unpack("!H", code)[0]]

def encryptPasswordICQ(password):
    key = [0xF3, 0x26, 0x81, 0xC4, 0x39, 0x86, 0xDB, 0x92, 0x71, 0xA3, 0xB9, 0xE6, 0x53, 0x7A, 0x95, 0x7C]
    bytes = map(ord, password)
    r = ""
    for i in range(len(bytes)):
        r = r + chr(bytes[i] ^ key[i % len(key)])
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

def readTLVsd(data):
    '''
    The same as big brother, but also return all data left after TLVs
    FIXME: 
        refactoring is really needed
    '''
    out = ''
    d = {}
    while data:
        head = detlv(data)
        d[head[0]] = data[4 : 4 + head[1]]
        data = data[4 + head[1]:]
        if data:
            out = data
    return (d, out)


#2a020d57002a 0001001700000000001700010003000200010003000100150001000400010006000100090001000a0001
#2A0200010036 0001001700000000000000010003000200010003000100040001000600010008000100090001000A0001000B0001000C000100130003
#             00010017000000000000

class Protocol:
    def __init__(self, gui = None, sock = None, connected = False):
        self._sock = sock
        self._gui = gui

        self.buf = ''
        self.statusindicators = 0x0000

        self._host = None
        self._port = None

        self._connected = connected
        self._groups = Group()

    def react(self, *kw, **kws):
        if self._gui is not None:
            self._gui.dispatch(kw, kws)

    def readConfig(self, config):
        self._config = config
        self._host, self._port = self._config.get('icq', 'host').split(':')
        self._port = int(self._port)

    def connect(self, host = None, port = None):
        if host is None:
            host = self._host
        if port is None:
            port = self._port
        self._sock = ISocket(host, port)
        self._sock.connect()
        log().log("Socket connected")

    def disconnect(self):
        self._sock.disconnect()
        self._sock = None
        self._host = None
        self._port = None
        self._connected = False

        self.react("Disconnected")

    def isConnected(self):
        return self._connected

    def send(self, data):
        self._sock.send(data)

    def read(self):
        return self._sock.read(10240)

    def sendFLAP(self, ch, data):
        header = "!cBHH"
        if (not hasattr(self, "seqnum")):
            self.seqnum = 0
        self.seqnum = (self.seqnum+1)%0xFFFF
        head = struct.pack(header,'*', ch, self.seqnum, len(data))

        data = head + str(data)
        log().packetout(data)
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

    def sendAuth(self, username = None):
        if username is None:
            username = self._config.get('icq', 'username')
        self.username = username
        encpass = encryptPasswordICQ(os.getenv("TEST_ICQ_PASS"))

        self.sendFLAP(0x01, '\000\000\000\001'+
            tlv(0x01, self.username)+
            tlv(0x02, encpass)+
            tlv(0x03, 'ICQ Inc. - Product of ICQ (TM).2001b.5.18.1.3659.85')+
            tlv(0x16, "\x01\x0a")+
            tlv(0x17, "\x00\x05")+
            tlv(0x18, "\x00\x12")+
            tlv(0x19, "\000\001")+
            tlv(0x1a, "\x0eK")+
            tlv(0x14, "\x00\x00\x00U")+
            tlv(0x0f, "en")+
            tlv(0x0e, "us"))

    def dispatch(self, ch):
        sfunc = "proc_%d_0_0" % ch

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

    def registrationRequest(self, password):
        '''
        SNAC(17,04)     CLI_REGISTRATION_REQUEST 
        Use this snac when you need new ICQ account (uin/password). 
        Server should reply with SNAC(17,05) containing new uin. 
        This snac mean that registration finished succesfully. 
        Server also can reply with SNAC(17,01) if it can't create new 
        user account.
        '''

        # 00 00 00 00     dword       just zeros  
        # 28 00      word        subcmd (request new uin)    
        # 03 00      word        sequence    
        # 00 00 00 00        dword       just zeros  
        # 00 00 00 00        dword       just zeros  
        # xx xx xx xx        dword       registration cookie 
        # xx xx xx xx        dword       registration cookie (the same)

        req =  "\x00\x00\x00\x00\x28\x00\x03\x00"
        req += "\x00\x00\x00\x00\x00\x00\x00\x00"

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

        log().packetin(data)

        count = struct.unpack('!H', data[0:2])[0]
        log().log('Received %d rate groups' % count)

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
            log().log("Class ID: " + str(info))
            dt = dt[35:]

        for ii in range(count):
            rgd, npair = struct.unpack('!HH', dt[:4])
            log().log("For family %d server has %d pairs" % (rgd, npair))

            # We want to send it back to server
            resp += struct.pack('!H', rgd)

            dt = dt[4:]
            for jj in range(npair):
                family, subfamily = struct.unpack('!HH', dt[4:8])
                self.outRateTable[family] = subfamily
                dt = dt[4:]

        log().log("Sending connection rate limits")
        self.sendSNAC(0x01, 0x08, 0, resp)

        time.sleep(SLEEP)
        log().log("Sending location rights limits")
        self.sendSNAC(0x02, 0x02, 0, '') # location rights info

    def proc_2_9_3(self, data):
        ''' BOS rights '''
        tlvs = readTLVs(data)
        self.maxPermitList = struct.unpack("!H", tlvs[1])[0]
        self.maxDenyList = struct.unpack("!H", tlvs[2])[0]
        log().log("Max permit list: %d, Max deny list: %d" % (self.maxPermitList, self.maxDenyList))

        time.sleep(SLEEP)
        log().log("Sending SSI rights info")
        self.sendSNAC(0x13, 0x02, 0, '')

    def proc_2_4_5(self, data):
        ''' ICBM parameters '''
        log().log("Sending changed default ICBM parameters command")
        self.sendSNAC(0x04, 0x02, 0, '\x00\x00\x00\x00\x00\x0b\x1f@\x03\xe7\x03\xe7\x00\x00\x00\x00')

        time.sleep(SLEEP)
        log().log("Sending PRM service limitations")
        self.sendSNAC(0x09, 0x02, 0, '')

    def proc_2_3_3(self, data):
        ''' Buddy list rights '''
        tlvs = readTLVs(data)
        self.maxBuddies = struct.unpack("!H", tlvs[1])[0]
        self.maxWatchers = struct.unpack("!H", tlvs[2])[0]
        log().log("Max buddies: %d, Max watchers: %d" % (self.maxBuddies, self.maxWatchers))

        log().log("Sending ICBM service parameters")
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
                version, toolID, toolVersion = sf[fam]
                d = d + struct.pack('!4H', fam, version, toolID, toolVersion)
        self.sendSNAC(0x01, 0x02, 0, d)

    def proc_2_1_15(self, data):
        ''' My status '''

        uinLen = int(struct.unpack('!B', data[0])[0])
        uin = str(data[1 : uinLen + 1])

        warningLevel, tlvNumber = struct.unpack('!HH', data[uinLen + 1: uinLen + 1 + 4])
        log().log('Got my status report: uin: %s, warning level: %d' %\
            (uin, warningLevel))

        tlvs = readTLVs(data[uinLen + 1 + 4:])
        self.parseSelfStatus(tlvs)

        log().log("Retrieving server-side contact list")
        self.sendSNAC(0x13, 0x04, 0, '')
#        self.getOfflineMessages()
#        self.sendSNAC(0x13, 0x05, 0, struct.pack('!LH', 0, 0))

    def proc_2_19_6(self, data):
        ''' This is the server reply to client roster 
        requests: SNAC(13,04) - Request contact list (first time),
        SNAC(13,05) - Contact list checkout.

        Server can split up the roster in several parts. This is 
        indicated with SNAC flags bit 1 as usual, however the "SSI 
        list last change time" only exists in the last packet. 
        And the "Number of items" field indicates the number of 
        items in the current packet, not the entire list. '''

        print 'PRE: ', ashex(data)
        print coldump(data)

        if __debug__:
            import cPickle
            f = open('string.dump', 'wb')
            cPickle.dump(data, f)
            f.close()

        ver = int(struct.unpack('!B', data[0:1])[0])
        assert ver == 0

        nitems = int(struct.unpack('!H', data[1:3])[0])
        print coldump(data[1:3])
        log().log("Items number: %d" % nitems)

        data = data[3:]

        # FIXME: still have a problems with parsing SSI items
        try:
            for ii in range(0, nitems):
                data = self.parseSSIItem(data)
        except Exception, msg:
            log().log("Exception while parsing SSI items")
            

        log().log('Current list of groups: %s' % self._groups)

    def parseSSIItem(self, data):

        print '*' * 10, "Parsing SSI data..."
        print coldump(data)

        itemLen = int(struct.unpack('>H', data[0:2])[0])
        data = data[2:]
        name = data[:itemLen]
        log().log("Length: %d, '%s'" % (itemLen, asPrintable(name)))

        data = data[itemLen:]

        groupID, itemID, flagType, dataLen = toints(struct.unpack('!4H', data[0:8]))

        log().log("groupID: %d, itemID: %d, flagType: %d (%s), dataLen: %d" % \
            (groupID, itemID, flagType, explainSSIItemType(flagType), dataLen))

        tlvs = readTLVs(data[8 : 8 + dataLen])

        # FIXME: only buddies processing 
        if flagType == SSI_ITEM_GROUP:
            self._groups.add(groupID, 'Some group')

        if flagType == SSI_ITEM_BUDDY:
            b = Buddy()

            # Setup it's GID right now
            b.gid = groupID

            for t in tlvs:
                tmp = "parseSSIItem_%02X" % t
                try:
                    func = getattr(self, tmp)
                    func(tlvs[t], b)

                    if b.name is None:
                        log().log("Buddy name is missing, replacing with UID")
                        b.name = name

                    log().log("Got new buddy from SSI list: %s" % b)

                    # OK, let's pass new buddy upto gui
                    self.react("New buddy", buddy = b)
                except AttributeError, msg:
                    log().log("Not fatal exception got: " + str(msg))

                    # Bad buddy, mark it as Null, do not add to list
                    b = None
                    break

            if b is not None:
                self._groups.addBuddy(groupID, b)

        else:
            for t in tlvs:
                tmp = "parseSSIItem_%02X" % t
                try:
                    func = getattr(self, tmp)
                    func(tlvs[t], flagType)
                except AttributeError, msg:
                    log().log("Not fatal exception got: " + str(msg))
     
        data = data[8 + dataLen:]
        return data

    def parseSSIItem_6D(self, t, b):
        '''
        Unknown
        '''
        log().log('Called unknown handler parseSSIItem_6D')

    def parseSSIItem_66(self, t, b):
        '''
        [TLV(0x0066), itype 0x00, size 00] - Signifies that you are 
        awaiting authorization for this buddy. The client is in charge 
        of putting this TLV, but you will not receiving status 
        updates for the contact until they authorize you, regardless 
        if this is here or not. Meaning, this is only here to tell 
        your client that you are waiting for authorization for the 
        person. This TLV is always empty.
        '''
        log().log("This client not yet authorized you")

    def parseSSIItem_145(self, t, b):
        '''
        [TLV(0x0145), itype 0x00, size XX] - 
        Date/time (unix time() format) when you send message to 
        this you first time. Actually I noticed that ICQLite adds 
        this TLV then you first open message dialog at this user. 
        Also I've seen this tlv in LastUpdateDate item.
        '''
        t = struct.unpack('!L', t)[0]
        b.firstMessage = t
        log().log("First time message: %s" % time.asctime(time.localtime(t)))

    def parseSSIItem_137(self, t, b):
        '''
        [TLV(0x0137), itype 0x00, size XX] - 
        Your buddy locally assigned mail address.
        '''
        b.email = t
        log().log("Buddy locally assigned mail address: %s" % t)

    def parseSSIItem_131(self, t, b):
        '''
        [TLV(0x0131), itype 0x00, size XX] - 
        This stores the name that the contact should show up as 
        in the contact list. It should initially be set to the 
        contact's nick name, and can be changed to anything by the client.
        '''
        b.name = t
        log().log("Buddy contact list name: %s" % t)

    def parseSSIItem_CA(self, t, flag):
        '''
        [TLV(0x00CA), itype 0x04, size 01] - 
        This is the byte that tells the AIM servers your privacy 
        setting. If 1, then allow all users to see you. If 2, then 
        block all users from seeing you. If 3, then allow only the 
        users in the permit list. If 4, then block only the users 
        in the deny list. If 5, then allow only users on your buddy list.
        '''
        log().log("AIM server privacy settings: %s" % str(t))

    def parseSSIItem_C8(self, t, flag):
        ''' [TLV(0x00C8), itype 0x01, size XX] - 
        If group is the master group, this contains the group 
        ID#s of all groups in the list. If the group is a normal 
        group, this contains the buddy ID#s of all buddies in the 
        group. Each ID# is 2 bytes. If there are no groups in the 
        list (if in the master group), or no buddies in the group 
        (if in a normal group), then this TLV is not present.
        '''
        log().log("Master group IDs: %s" % str(t))

    def proc_2_3_12(self, data):
        ''' Server send this when user from your contact list goes 
        offline. See also additional information about online userinfo block.'''

        log().log("Called 2,3,12 with data:")
        log().log(coldump(data))

    def proc_2_3_11(self, data):
        ''' Server sends this snac when user from your contact list 
        goes online. Also you'll receive this snac on user status 
        change (in this case snac doesn't contain TLV(0xC)). 
        See also additional information about online userinfo block. '''

        uinLen = int(struct.unpack('!B', data[0])[0]) 
        uin = data[1 : uinLen]
        log().log("User '%s' is online" % uin)
        log().log("UIN length: %d, UIN: %s" % (uinLen, uin))

        data = data[1 + uinLen:]

        warningLevel = int(struct.unpack('!H', data[0:2])[0]) 
        ntlv = int(struct.unpack('!H', data[2:4])[0]) 
        log().log("Warning level: %d. number of TLV: %d" % (warningLevel, ntlv))

        tlvs = readTLVs(data[4:])
        userClass = int(struct.unpack('!H', tlvs[0x01])[0])

        # TLV.Type(0x0C) - dc info (optional)
        try:
            dc = tlvs[0x0c]

            internalIP = socket.inet_ntoa(dc[0 : 4])
            internalPort = int(struct.unpack('!L', dc[4 : 8])[0])

            log().log("Internal IP: %s:%d" % (internalIP, internalPort))

            dcType = int(struct.unpack('!B', dc[8 : 9])[0])
            t = self.parseDcType(dcType)
            log().log("DC type: %s" % t)

            dc = dc[9:]
            dcProtocolVersion = int(struct.unpack('!H', dc[0 : 2])[0])
            dcAuthCookie = int(struct.unpack('!L', dc[2 : 6])[0])
            webFrontPort = int(struct.unpack('!L', dc[6 : 10])[0])
            clientFutures = int(struct.unpack('!L', dc[10 : 14])[0])

            log().log("dcProtocolVersion: %d, dcAuthCookie: %d, webFrontPort: %d, clientFutures: %d" % \
                (dcProtocolVersion, dcAuthCookie, webFrontPort, clientFutures))

            assert clientFutures == 0x03

            lastInfoUpdate = int(struct.unpack('!L', dc[14 : 18])[0])
            lastExtInfoUpdate = int(struct.unpack('!L', dc[18 : 22])[0])
            lastExtStatusUpdate = int(struct.unpack('!L', dc[22 : 26])[0])

#           What's format for this time? Fails.
#            print "lastInfoUpdate: %s, lastExtInfoUpdate: %s, lastExtStatusUpdate: %s" % \
#                (time.asctime(time.localtime(lastInfoUpdate)), time.asctime(time.localtime(lastExtInfoUpdate)), time.asctime(time.localtime(lastExtStatusUpdate)))

            junk = int(struct.unpack('!H', dc[26 : 28])[0])
        except:
            raise

        # TLV.Type(0x0A) - external ip address
        externalIP = "0:0:0:0"
        try:
            externalIP = socket.inet_ntoa(tlvs[0x0a][0 : 4])
        except Exception, msg:
            pass # FIXME
        log().log("External IP: %s" % externalIP)

        # TLV.Type(0x06) - user status
        userStatus = tlvs[0x06][0 : 4]
        status = self.parseUserStatus(userStatus)
        log().log("User status: %s" % status)

        # TLV.Type(0x0D) - user capabilities
        try:
            caps = tlvs[0x0d]
            log().log("User capabilities: " + ashex(caps))
        except KeyError, msg:
            log().log("Unable to get user capabilities")
            
        # TLV.Type(0x0F) - online time
        onlineTime = int(struct.unpack('!L', tlvs[0x0f][0 : 4])[0])
        log().log("Online time: " + time.asctime(time.localtime(onlineTime)))

        # TLV.Type(0x03) - signon time
        singonTime = int(struct.unpack('!L', tlvs[0x03][0 : 4])[0])
        log().log("Signon time: " + time.asctime(time.localtime(singonTime)))

        # TLV.Type(0x05) - member since
        try:
            memberSince = int(struct.unpack('!L', tlvs[0x05][0 : 4])[0])
            log().log("Member since: " + time.asctime(time.localtime(memberSince)))
        except KeyError, msg:
            log().log("Unable to get 'member since' information")

        # TLV.Type(0x11) - times updated
        # FIXME: not parsed yet
        try:
            tlv = tlvs[0x11]
        except KeyError, msg:
            log().log("Unable to get 'times updated' information")

        # TLV.Type(0x19) - new-style capabilities list
        try:
            caps = tlvs[0x19]
            log().log("User (AIM) capabilities: " + ashex(caps))
        except KeyError, msg:
            log().log("Unable to get user (AIM) capabilities")

        # TLV.Type(0x1D) - user icon id & hash
        try:
            icon = tlvs[0x1d]
            iconID = struct.unpack('!H', icon[0 : 2])
            iconFlags = struct.unpack('!B', icon[2 : 3])
            iconHash = struct.unpack('!B', icon[3 : 4])

            log().log("Icon ID: %d" % (iconID))
        except KeyError, msg:
            log().log("Unable to get user icon")

    def parseUserStatus(self, status):
        st = []
        p1, p2 = struct.unpack('!HH', status)
        for s in _userStatusP1:
            if s & p1:
                st.append(_userStatusP1[s])
        for s in _userStatusP2:
            if s & p2:
                st.append(_userStatusP2[s])
        return ', '.join(st)

    def parseDcType(self, dcType):
        t = []
        for dc in _directConnectionType:
            if dc & dcType:
                t.append(_directConnectionType[dc])
        return ', '.join(t)
 
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
        log().log("User class: " + ' '.join(out))

    def proc_2_4_1(self, data):
        '''
        SNAC(04,01)     SRV_ICBM_ERROR      

        This snac mean that server can't send your message to recipient 
        because it invalid, too large, wrong type or not supported by 
        receiver. See also SNAC(04,0A), SNAC(04,0C) for more info. 
        Most used error types:

        0x04 - you are trying to send message to offline client ("")
        0x09 - message not supported by client
        0x0E - your message is invalid (incorrectly formated)
        0x10 - receiver/sender blocked
        '''
        errorCode = int(struct.unpack('!H', data[0:2])[0])
        tlvs = readTLVs(data[2:])

        subErrorCode = 0
        try:
            subErrorCode = int(struct.unpack('!H', tlvs[0x08])[0])
        except KeyError, msg:
            log().log("No error subcode found")

        log().log("Can't send your message to recipient (%d, %d) (%s)" %\
            (errorCode, subErrorCode, _msg_error_codes[errorCode]))

    def proc_2_4_10(self, data):
        ''' SNAC(04,0A)     SRV_MISSED_MESSAGE      

        This snac mean that somebody send you a message but server 
        can't deliver it to you for some reason. It contain information 
        about user, who send you a message, number of missed messages and 
        reason. Known reason types: 

        0 - Message was invalid
        1 - Message was too large
        2 - Message rate exceeded
        3 - Sender too evil (sender warn level > your max_msg_sevil)
        4 - You are too evil (sender max_msg_revil > your warn level)
        '''

        log().log("Missed message")

        messageType = int(struct.unpack('!H', data[0:2])[0])
        uinLen = int(struct.unpack('!B', data[2:3])[0])
        uin = data[3 : 3 + uinLen]
        data = data[3 + uinLen:]
        warningLevel = int(struct.unpack('!H', data[0:2])[0])
        tlvNumber = int(struct.unpack('!H', data[2:4])[0])

        assert tlvNumber == 4

        log().log("MessageType: %d, uin: %s, Warning level: %d"\
            % (messageType, uin, warningLevel))

        tlvs, rest = readTLVsd(data[4:])

        missedMessages = int(struct.unpack('!H', rest[0:2])[0])
        reason = int(struct.unpack('!H', rest[2:4])[0])

        log().log("Missed messages: %d, Reason: %s" %\
            (missedMessages, explainReason(reason)))

    def proc_2_4_7(self, data):
        ''' Message received '''
        cookie = data[0:7]
        messageChannel = int(struct.unpack('!H', data[8:10])[0])
        snameLen = int(struct.unpack('!B', data[10])[0])
        sname = data[11:11 + snameLen]
        data = data[11 + snameLen:]

        log().log('Got message, channel: %d, from: %s' % 
            (messageChannel, sname))

        senderWarningLevel = int(struct.unpack('!H', data[0:2])[0])
        tlvNumber = int(struct.unpack('!H', data[2:4])[0])

        tlvs = readTLVs(data[4:])

        userClass = int(struct.unpack('!H', tlvs[1])[0])
        try:
            userStatus = int(struct.unpack('!L', tlvs[6])[0])
        except KeyError, msg:
            log().log("Unable to fetch user status")

        try:
            accCreationTime = int(struct.unpack('!L', tlvs[3])[0])
        except KeyError, msg:
            log().log("Unable to fetch account creation time")

        try:
            clientIdleTime = int(struct.unpack('!L', tlvs[0x0f])[0])
        except KeyError, msg:
            log().log("Unable to fetch client idle time")

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
        log().log("You-were-added from " + uin)

    def parseMessageType(self, mtype):
        out = []
        for t in _messageTypes:
            if t & mtype: out.append(_messageTypes[t])
        log().log("Message type: " + " ".join(out))

    def parseMessageFlags(self, mflags):
        out = []
        for t in _messageFlags:
            if t & mflags: out.append(_messageFlags[t])
        log().log("Message flags: " + " ".join(out))

    def proc_2_4_7_4(self, tlvs):
        '''  Channel 4 message format (plain-text messages) '''
        t = tlvs[0x05]
        uin = int(struct.unpack('<L', t[0:4])[0])
        mtype = int(struct.unpack('!B', t[4:5])[0])
        mflags = int(struct.unpack('!B', t[5:6])[0])
        ln = int(struct.unpack('<H', t[6:8])[0])
        msg = t[8:]

        log().log("Message type 4, UIN: %d, length: %d, contents: %s"
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

        log().log('Message type 1: ' + str(msg))

    def proc_2_2_3(self, data):
        ''' Client service parameters request '''
        tlvs = readTLVs(data)
        self.maxProfileLength = struct.unpack('!H', tlvs[1])[0]
        self.maxCapabilities = struct.unpack('!H', tlvs[2])[0]
        log().log("MaxProfileLength: %d, MaxCapabilities: %d" %
            (self.maxProfileLength, self.maxCapabilities))

        self.capabilities = [caps.ICQ, caps.RELAY, caps.UTF8]

        tlvs = tlv(5, ''.join(self.capabilities))

        log().log("Sending client capabilities")
        self.sendSNAC(0x02, 0x04, 0, tlvs)

        # Client use this SNAC to request buddylist service parameters 
        # and limitations. Server should reply via SNAC(03,03).

        time.sleep(SLEEP)
        log().log("Sending buddylist service parameters ")
        self.sendSNAC(0x03, 0x02, 0, '')

    def proc_4_9_2(self, data):
        ''' You have been disconnected from the ICQ network because you 
        logged on from another location using the same ICQ number. '''
        self.disconnect()
        log().log("You have been disconnected from the ICQ network because you logged on from another location using the same ICQ number.")

    def proc_1_0_0(self, data):
        log().log("Logging in...")

    def CLI_FIND_BY_UIN2(self):
        log().log("CLI_FIND_BY_UIN2")
        tlvs = tlv(0x01, struct.pack())

    def CLI_WHITE_PAGES_SEARCH2(self):
        log().log("CLI_WHITE_PAGES_SEARCH2")

    def getOfflineMessages(self):
        ''' Client sends this SNAC when wants to retrieve messages 
        that was sent by another user and buffered by server during 
        client was offline. '''

        tlvs = tlv(0x01, '\x00\x08' + struct.pack("<L", int(username)) + '\x3c\x00\x02\x00')
        self.sendSNAC(0x15, 0x02, 0, tlvs)

    def login(self, mainLoop = False):
        log().log('Logging in...')
        self.react('Login')

        buf = self.read()
        log().packetin(buf)

        log().log('Sending credentials')
        self.sendAuth()
        buf = self.read()
        log().packetin(buf)

        snac = self.readSNAC(buf)
        i=snac[5].find("\000")
        snac[5]=snac[5][i:]
        tlvs=readTLVs(snac[5])
        log().log(tlvs)

        if tlvs.has_key(TLV_ErrorCode):
            log().log("Error: " + explainError(tlvs[TLV_ErrorCode]))

        server = ''
        if tlvs.has_key(TLV_Redirect):
            server = tlvs[TLV_Redirect]
            log().log("Redirecting to: " + server)

        self._sock.disconnect()

        self._host, self._port = server.split(':')
        self._port = int(self._port)

        # ===============
        self.connect()

        # ================================
        buf = self.read()
        log().packetin(buf)

        self.sendFLAP(0x01, '\000\000\000\001' + tlv(0x06, tlvs[TLV_Cookie]))

        log().log('Login done')
        self.react('Login done')

        if mainLoop:
            log().log('Going to main loop')
            self.mainLoop()

    def mainLoop(self):
        # self.keepGoing must be extenrally created or defined in derived class
        while self.keepGoing:
            buf = self.read()
            log().packetin(buf)

            ch, b, c = self.readFLAP(buf)
            snac = self.readSNAC(c)
            log().log('going to call proc_%d_%d_%d' % (ch, snac[0], snac[1]))
            log().log('for this snac: ' + snac)

            tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
            func = getattr(self, tmp)

            func(snac[5])

    def sendMessage(self, message, thruServer = True, ack = False,
        autoResponse = False, offline = False):

        # Channel 1       Channel 1 message format (plain-text messages) 
        # Channel 2       Channel 2 message format (rtf messages, rendezvous)    
        # Channel 4       Channel 4 message format (typed old-style messages)

        user = message.getUser()
        log().log("Sending message to " + user)

#        print '*************************'
#        print 'sending to 177033621 istead of', user
#        user = '177033621'

        channel = 1
        channel = struct.pack('!H', channel)
        data = genCookie() + channel + struct.pack('!B', len(user)) + user

        # 05      byte        fragment identifier (array of required capabilities)    
        # 01     byte        fragment version    
        # xx xx      word        Length of rest data 
        # xx ...     array       byte array of required capabilities (1 - text)

        # 01      byte        fragment identifier (text message)  
        # 01     byte        fragment version    
        # xx xx      word        Length of rest data
        t = "\x05\x01\x00\x03\x01\x01\x02"

        # 00 00      word        Message charset number  
        # ff ff      word        Message language number 
        # xx ..      string (ascii)      Message text string

        charSet = 3
        charSubSet = 0
        t += '\x01\x01' + struct.pack('!3H', len(message.getContents()) + 4, charSet, charSubSet)
        t += message.getContents()

        outMsg = data + tlv(2, t)

        if ack:
            outMsg = outMsg + tlv(3, '')
        if autoResponse:
            outMsg = outMsg + tlv(4, '')
        if offline:
            outMsg = outMsg + tlv(6, '')

        self.sendSNAC(0x04, 0x06, 0, outMsg)


def _test():

#    s = ISocket('login.icq.com', 5190)
#    s.connect()

    p = Protocol()
    p.connect('login.icq.com', 5190)

    buf = p.read()
    log().packetin(buf)

    p.sendAuth(username)
    buf = p.read()
    log().packetin(buf)

    snac = p.readSNAC(buf)
    i=snac[5].find("\000")
    snac[5]=snac[5][i:]
    tlvs=readTLVs(snac[5])
    log().log(tlvs)

    if tlvs.has_key(TLV_ErrorCode):
        log().log("Error: " + explainError(tlvs[TLV_ErrorCode]))

    server = ''
    if tlvs.has_key(TLV_Redirect):
        server = tlvs[TLV_Redirect]
        log().log("Redirecting to: " + server)

    p.disconnect()
    host, port = server.split(':')

    # ===============
    s = ISocket(host, int(port))
    s.connect()
    p = Protocol(sock = s, connected = True)

    # ================================
    buf = p.read()
    log().packetin(buf)

    p.sendFLAP(0x01, '\000\000\000\001' + tlv(0x06, tlvs[TLV_Cookie]))

    # ================================

    while p.isConnected():
        buf = p.read()
        log().packetin(buf)
        print coldump(buf)

        ch, b, c = p.readFLAP(buf)
        snac = p.readSNAC(c)
        print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
        print 'for this snac: ', snac

        tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
        func = getattr(p, tmp)

        func(snac[5])

if __name__ == '__main__':
    _test()

# ---
