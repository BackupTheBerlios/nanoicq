#!/bin/env python2.4

#
# $Id: icq.py,v 1.106 2006/11/24 13:35:19 lightdruid Exp $
#

import sys
import os
import time
import struct
import socket
import types
import cStringIO
import traceback
import datetime

#socket.setdefaulttimeout(1.0)

from utils import *
from snacs import *
from isocket import ISocket

from buddy import Buddy
from group import Group, NotFound
from history import History
import HistoryDirection

import caps
from logger import log, init_log, LogException
from message import messageFactory, MessageQueue
from proxy import *
from nqueue import nqueue

_default_reject_reason = 'Your authorization request is rejected, reason unknown'

init_log([sys.stdout, open('nanoicq.log', 'wb')])

# for debug only
SLEEP = 0

# socket read buffer size (bytes)
_SOCK_BUFFER = 1024000

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

_motdTypes = {
0x0001:      "MTD_MDT_UPGRAGE",     # Mandatory upgrade needed notice   
0x0002:      "MTD_ADV_UPGRAGE",     # Advisable upgrade notice  
0x0003:      "MTD_SYS_BULLETIN",    # AIM/ICQ service system announcements  
0x0004:      "MTD_NORMAL",          # Standart notice   
0x0006:      "MTD_NEWS",            # Some news from AOL service
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

MTYPE_AUTHREQ =    0x06
MTYPE_AUTHDENY =   0x07
MTYPE_AUTHOK =     0x08

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
  0x0000:      "online", #       Status is online  
  0x0001:      "away", #     Status is away    
  0x0002:      "dnd", #      Status is no not disturb (DND)    
  0x0004:      "na", #       Status is not available (N/A) 
  0x0010:      "occupied", #     Status is occupied (BUSY) 
  0x0020:      "free", #        Status is free for chat   
  0x0100:      "invisible", #        Status is invisible
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
    return struct.pack("!HH", typ, len(val)) + val

def tlv_le(typ, val):
    return struct.pack("<HH", typ, len(val)) + val

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


class Protocol:
    _groupsFile = 'groups.nanoicq'

    def __init__(self, gui = None, sock = None, connected = False):
        self._sock = sock
        self._gui = gui

        self.buf = ''
        self.statusindicators = 0x0000

        self._host = None
        self._port = None

        self._connected = connected
        if os.path.exists(self._groupsFile):
            self._groups = Group.load(self._groupsFile)
        else:
            self._groups = Group(self._groupsFile)

        self._currentUser = None
        self._offlineMessageQueue = MessageQueue()

    def saveState(self):
        # FIXME:
        #self._groups.save()
        pass

    def react(self, *kw, **kws):
        nqueue().put( (kw, kws) )
        #if self._gui is not None:
        #    self._gui.dispatch(kw, kws)

    def readConfig(self, xmlConfig):
        self._xmlConfig = xmlConfig
        self._host = self._xmlConfig.get("./Options/Network/ICQ/LoginServer")
        self._port = self._xmlConfig.getInt("./Options/Network/ICQ/Port")

    def getColorSet(self):
        '''
        FIXME: actually it's ugly, it makes sense to
        wrap it to something more suitable.

        Returns 4-list, bg/fg for incoming messages and
        bg/fg for outgoing messages
        '''

        ibg = self._xmlConfig.get("./Options/IncomingBackground")
        ifg = self._xmlConfig.get("./Options/IncomingForeground")

        obg = self._xmlConfig.get("./Options/OutgoingBackground")
        ofg = self._xmlConfig.get("./Options/OutgoingForeground")

        return [ibg, ifg, obg, ofg]

    def connect(self, host = None, port = None):
        if host is None:
            host = self._host
        if port is None:
            port = self._port

        self.default_charset = None
        try:
            self.default_charset = self._xmlConfig.get("./Options/Network/ICQ/DefaultCharset")
        except AttributeError, msg:
            # We don't have config, use default values
            pass

        log().log("Connecting to %s:%d" % (host, port))

        if hasattr(self, 'xmlConfig') and self._xmlConfig.get("./Options/Network/ICQ/ProxyServer"):
            junk = self._xmlConfig.get("./Options/Network/ICQ/ProxyServer")
            proxyHost = junk[0]
            proxyPort = int(junk[1])

            proxyType = self._xmlConfig.get("./Options/Network/ICQ/ProxyType").capitalize()
            print 'Using: ', proxyType
            self._sock = eval("%sProxy(proxyHost, proxyPort, self.default_charset)" % proxyType)
            self._sock.connect(host, port)
        else:
            self._sock = ISocket(host, port, self.default_charset)
            self._sock.connect()

        log().log("Socket connected")

    def disconnect(self):
        self._sock.disconnect()
        self._sock = None
        self._connected = False

        self.react("Disconnected")

    def isConnected(self):
        return self._connected

    def send(self, data):
        try:
            self._sock.send(data)
        except Exception, exc:
            log().log('socket send got exception ' + str(exc))
            raise

    def read(self):
        return self._sock.read()

    def sendFLAP(self, ch, data):
        header = "!cBHH"
        if (not hasattr(self, "seqnum")):
            self.seqnum = 0
        self.seqnum = (self.seqnum + 1) % 0xFFFF
        head = struct.pack(header, '*', ch, self.seqnum, len(data))

        try:
            data = head + data
        except UnicodeEncodeError, msg:
            data = head + data.encode(self.default_charset)

        log().packetout_col(data)
        self.send(data)

    def readFLAP(self, buf):
        header = "!cBHH"
        if len(buf) < 6:
            print 'len(buf) < 6', len(buf) < 6
            return
        flap = struct.unpack(header, buf[:6])

        # ========================
        #if len(buf) < 6 + flap[3]:
        #    print 'len(buf) < 6 + flap[3]', len(buf) < 6 + flap[3]
        #    print 'len(buf), flap[3]', len(buf), int(flap[3])
        #    return
        # ========================

        data, buf = buf[6:6 + flap[3]], buf[6 + flap[3]:]
        return [flap[1], buf, data]

    def encodeSNAC(self, family, subfamily, id, data):
        return struct.pack("!HHBBL", family, subfamily, 0, 0, id) + data

    def sendSNAC(self, family, subfamily, id, data):
        self.sendFLAP(0x02, self.encodeSNAC(family, subfamily, id, data))

    def sendSNAC_C(self, ch, family, subfamily, id, data):
        ''' Send SNAC using specific channel
        '''
        self.sendFLAP(ch, self.encodeSNAC(family, subfamily, id, data))

    def readSNAC(self, data):
        return list(struct.unpack("!HHBBL", data[:10])) + [data[10:]]

    def sendCliHello(self):
        '''
        The packet sent upon establishing a connection. 
        If the client wants to login to login.icq.com, it sends all 
        TLVs (CLI_IDENT) except TLV(6), which is for login to the 
        redirected server (CLI_COOKIE). 
        * To request a new UIN, no TLV is sent (CLI_HELLO). *
        '''
        self.sendFLAP(0x01, '\000\000\000\001')

    def sendAuth(self, username = None):
        if username is None:
            username = self._xmlConfig.get("./Options/Network/ICQ/ICQNumber")
        self.username = username

        encpass = encryptPasswordICQ(self._xmlConfig.get("./Options/Network/ICQ/ICQPassword"))

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
        ''' Initiate new UIN registration
        '''

        # Then assembly resuest and send it, it must include
        # only our password
        r = ''
        r += '\x00\x00\x00\x00'
        r += '\x28\x00\x03\x00'
        r += '\x00\x00\x00\x00'
        r += '\x00\x00\x00\x00'

        r += '\x03\x46\x00\x00'
        r += '\x03\x46\x00\x00'

        r += '\x00\x00\x00\x00'
        r += '\x00\x00\x00\x00'
        r += '\x00\x00\x00\x00'
        r += '\x00\x00\x00\x00'

        r += struct.pack("<H", len(password)) + password + '\x00'
        r += '\x03\x46\x00\x00'
        r += '\x00\x00'
        r += '\x03\x02'

        self.sendSNAC(0x17, 0x04, 0, tlv(1, r))

    def registrationImageRequest(self):
        ''' SNAC(17,0C) Request picture for registration?
        2a 02 3e fd 00 0a 00 17-00 0c 00 00 00 00 00 0c 
        '''
        data = '\x00\x00\x00\x00'
        data += '\x00\x0C'

        self.sendSNAC(0x17, 0x0C, 0, data)

    def registrationImageResponse(self, imageText, password):

        data = '\x00\x01'

        data += struct.pack("!H", 51 + len(password))
        data += '\x00\x00\x00\x00'
        data += '\x28\x00\x03\x00'

        data += '\x00\x00\x00\x00'
        data += '\x00\x00\x00\x00'
        data += '\x94\x68\x00\x00'
        data += '\x94\x68\x00\x00'

        data += '\x00\x00\x00\x00'
        data += '\x00\x00\x00\x00'
        data += '\x00\x00\x00\x00'
        data += '\x00\x00\x00\x00'

        data += str(struct.pack("<H", len(password) + 1))
        data += str(password) 
        data += '\x00'

        data += '\x94\x68\x00\x00'

        #data += '\xf2\x07\x00\x00'
        data += '\x00\x00\x06\x02'

        data += '\x00\x09'
        data += str(struct.pack("!H", len(imageText)))
        data += str(imageText)

        self.sendSNAC(0x17, 0x04, 4, data)

        buf = self.read()
        print coldump(buf)

        ch, b, c = self.readFLAP(buf)
        snac = self.readSNAC(c)

        print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
        print 'for this snac: ', snac

        tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
        flag1, flag2 = snac[2], snac[3]
        func = getattr(self, tmp)

        func(snac[5], flag2)

    def proc_2_23_1(self, data, flag):
        '''
        SNAC(17,01)     SRV_REGISTRATION_ERROR  

        Server replies with this SNAC to SNAC(17,04) - client 
        registration request. This snac mean that registration failed for 
        some reason. 
        '''
        log().log("Got SNAC(17,01)     SRV_REGISTRATION_ERROR")
        errorCode = struct.unpack('!H', data[0:2])
        try:
            errorString = _msg_error_codes[errorCode]
        except Exception, msg:
            errorString = "Unknown error code: %d" % errorCode
        log().log(errorString)

        self.react("Registration error", err = errorString)

    def proc_2_23_5(self, data, flag):
        '''
        SNAC(17,05), Server confirms CAPTCHA picture text is valid
        '''
        log().log("New UIN request approved by server")

        tlvs = readTLVs(data)
        if not tlvs.has_key(0x01):
            log().log("Bad response from server (missing TLV(0x01)):")
            log().log(coldump(data))
            return

        d = tlvs[0x01]

        d = d[10:]
        port = int(struct.unpack('!L', d[0:4])[0])
        addr = socket.inet_ntoa(d[4:8])
        log().log("New UIN request was sent from %s:%d" % (addr, port))

        d = d[8+4:]
        cookie1 = d[:4]

        d = d[4*5:]
        uin = str(int(struct.unpack("<L", d[:4])[0]))
        log().log("New UIN: " + uin)

        d = d[4:]
        cookie2 = d[:4]

        self.react("New UIN", uin = uin)

    def proc_2_23_13(self, data, flag):
        '''
        SNAC(17,0D), Server send CAPTCHA picture after registration request
        http://www.captcha.net/
        '''

        tlvs = readTLVs(data)
        dump2file('tlvs.req', tlvs[2])

        if not tlvs.has_key(0x01) or not tlvs.has_key(0x02):
            raise Exception("Unknown registration seuqnce response (expected CAPTCHA picture)")
        if tlvs[0x01] != 'image/jpeg':
            raise Exception("Unknown format of registration CAPTCHA picture (%s)" % tlvs[0x01])

        # FIXME: decouple from wx!
        import wx
        img = wx.ImageFromStream(cStringIO.StringIO(tlvs[0x02]))
        self.react("Got CAPTCHA", image = img)

    def searchByName(self, ownerUin, nick, first, last):
        '''
        SNAC(15,02)/07D0/055F   CLI_WHITE_PAGES_SEARCH2 

        This is client tlv-based white pages search request used by ICQ2001+. 
        Server should respond with 1 or more packets. Last reply packet 
        allways SNAC(15,03)/07DA/01AE, other reply packets 
        SNAC(15,03)/07DA/01A4. See also list of TLVs that modern 
        clients use in TLV-based requests.
        '''

        data2 = ''
        if len(nick) > 0:
            data2 += tlv_le(0x0154, struct.pack('<H', len(nick)) + nick + "\x00")
        if len(first) > 0:
            data2 += tlv_le(0x0140, struct.pack('<H', len(first)) + first + "\x00")
        if len(last) > 0:
            data2 += tlv_le(0x014A, struct.pack('<H', len(last)) + last + "\x00")

        data = struct.pack('<L', int(ownerUin))
        data += "\xd0\x07\x02\x00\x5f\x05"
        data += str(data2)

        data = struct.pack('<H', len(data)) + data

        log().log("Sending name search request for '%s', '%s', '%s'" % (nick, first, last))
        self.sendSNAC(0x15, 0x02, 0, tlv(0x01, data))

    def searchByEmail(self, ownerUin, email):
        '''
        SNAC(15,02)/07D0/0573   CLI_FIND_BY_EMAIL3 

        This is client search by email tlv-based request used by ICQ2001+. 
        Server should respond with 1 or more packets. Last reply packet 
        allways SNAC(15,03)/07DA/01AE, other reply packets 
        SNAC(15,03)/07DA/01A4. See also list of TLVs that modern clients 
        use in TLV-based requests.
        '''

        data = struct.pack('<L', int(ownerUin))
        data += "\xd0\x07\x00\x4C\x73\x05"

        data2  = struct.pack('<H', len(email))
        data2 += str(email) + "\x00"

        data += tlv_le(0x015E, data2)
        data = struct.pack('<H', len(data)) + data

        log().log("Sending email search request for " + email)
        self.sendSNAC(0x15, 0x02, 0, tlv(0x01, data))

    def searchByUin(self, ownerUin, uin):
        '''
        SNAC(15,02)/07D0/051F   CLI_FIND_BY_UIN     

        This is client search by uin request. Server should respond with 
        last search found record SNAC(15,03)/07DA/01AE because uin 
        number is unique. '''

        data = struct.pack('<L', int(ownerUin))
        data += "\xd0\x07\x02\x00\x1f\x05"
        data += struct.pack('<L', int(uin))
        data = struct.pack('<H', len(data)) + data

        log().log("Sending UIN search request for " + uin)
        self.sendSNAC(0x15, 0x02, 0, tlv(0x01, data))

    def proc_2_1_19(self, data, flag):
        '''
        SNAC(01,13)     SRV_MOTD    

        Server send this during protocol negotiation sequence. 
        Various docs call this SNAC as "message of the day" but it looks 
        like that ICQ2K+ ignores this SNAC completely.
        '''
        typ = struct.unpack('!H', data[0 : 2])[0]
        mtype = self._decodeMotdType(typ)
        tlvs = readTLVs(data[2:])

        log().log('Got (01,13) MOTD message: ' + mtype)
        if tlvs.has_key(0x0b):
            log().log('MOTD message contents: ' + tlvs[0x0b])

    def _decodeMotdType(self, typ):
        out = []
        for t in _motdTypes:
            if typ & t:
                out.append(_motdTypes[t])
        return ', '.join(out)

    def proc_2_1_3(self, data, flag):
        '''
        SNAC(01,03)     SRV_FAMILIES  

        This is the first snac in protocol negotiation sequence. 
        Client shouldn't use families not listed in this SNAC. 
        See also known families list. So if your client use SNAC(13) family 
        and server SNAC(01,03) doesn't contain it - your client should 
        popup "server error" message when user want's to change server-stored 
        information (SSI). 
        '''
        log().log('(01,03) Got SRV_FAMILIES')
        self.parseFamilies(data)
        self.families = supported

        out = ''
        for f in self.serverFamilies:
            if self.families.has_key(f):
                out += struct.pack("!2H", f, self.families[f])

        '''
        SNAC(01,17)     CLI_FAMILIES_VERSIONS  

        This is the client response to SNAC(01,03). 
        This snac contain families versions which client want's from server. 
        Server should respond with SNAC(01,18). 
        Client sends this SNAC during protocol negotiation sequence. 
        See also known families list. 
        '''
        log().log('Sending (01,17) CLI_FAMILIES_VERSIONS')
        self.sendSNAC(0x01, 0x17, 0, out)

    def proc_2_1_24(self, data, flag):
        '''
        SNAC(01,18)     SRV_FAMILIES_VERSIONS  

        This is the server response to SNAC(01,17). 
        This snac contain families versions which server supports. 
        Server sends this SNAC during protocol negotiation sequence. 
        See also known families list. 
        '''
        log().log('Got (01,18) SRV_FAMILIES_VERSIONS')

        '''
        SNAC(01,06)     CLI_RATES_REQUEST  

        Client use this SNAC to request server rate-limits. 
        This happens during protocol negotiation sequence. 
        Server should reply via SNAC(01,07).
        '''
        log().log('Sending (01,06) CLI_RATES_REQUEST')
        self.sendSNAC(0x01, 0x06, 0, '')

    def proc_2_1_7(self, data, flag):
        '''
        SNAC(01,07)     SRV_RATE_LIMIT_INFO  

        This snac contain server information about its snac-rate 
        limitations. You can read rate limits detailed information here. 
        See also SNAC(01,0A) for more info.
        '''

        log().log('Got (01,07) SRV_RATE_LIMIT_INFO')
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

        log().log("Sending (01,08) CLI_RATES_ACK connection rate limits")
        self.sendSNAC(0x01, 0x08, 0, resp)

        time.sleep(SLEEP)
        log().log("Sending (02,02) CLI_LOCATION_RIGHTS_REQ location rights limits")
        self.sendSNAC(0x02, 0x02, 0, '') # location rights info

    def proc_2_9_3(self, data, flag):
        '''
        SNAC(09,03)     SRV_PRIVACY_RIGHTS_REPLY 

        Server replies with this SNAC to SNAC(09,02) - client service 
        parameters request.

        '''
        log().log('Got (09,03) SRV_PRIVACY_RIGHTS_REPLY')
        tlvs = readTLVs(data)
        self.maxPermitList = struct.unpack("!H", tlvs[1])[0]
        self.maxDenyList = struct.unpack("!H", tlvs[2])[0]
        log().log("Max permit list: %d, Max deny list: %d" % (self.maxPermitList, self.maxDenyList))

        '''
        SNAC(13,02)     CLI_SSI_RIGHTS_REQUEST 

        Use this to request server-stored information (SSI) service 
        limitations. Server should reply via SNAC(13,03), that contain 
        limitations for server-stored information items. 
        '''
        time.sleep(SLEEP)
        log().log("Sending (13,02) CLI_SSI_RIGHTS_REQUEST, SSI rights info")
        self.sendSNAC(0x13, 0x02, 0, '')

    def proc_2_4_5(self, data, flag):
        '''  
        SNAC(04,05)     SRV_ICBM_PARAMS  

        This is the server reply for SNAC(04,04). It contain client icbm 
        parameters like channel, max_msgsize, max_sender_evil, 
        max_receiver_evil. If "channel" parameter = 0 client want's to set 
        parameters for all available message channels. 
        See also SNAC(04,01) for more information. 
        '''
        log().log('Got SNAC(04,05) SRV_ICBM_PARAMS')

        '''
        SNAC(04,02)     CLI_SET_ICBM_PARAMS  

        Client use this snac to set its icbm parameters like max_msgsize, 
        max sender_evil... You can request these parameters from server 
        using SNAC(04,04). Server will reply via SNAC(04,05). 
        See also SNAC(04,01) for more information. 
        '''
        log().log("Sending (04,02) CLI_SET_ICBM_PARAMS - changed default ICBM parameters command")
        self.sendSNAC(0x04, 0x02, 0, '\x00\x00\x00\x00\x00\x0b\x1f@\x03\xe7\x03\xe7\x00\x00\x00\x00')

        '''
        SNAC(09,02)     CLI_PRIVACY_RIGHTS_REQ  

        Client use this SNAC to request buddylist service parameters and limitations.
        '''
        log().log("Sending (09,02) CLI_PRIVACY_RIGHTS_REQ  - PRM service limitations")
        time.sleep(SLEEP)
        self.sendSNAC(0x09, 0x02, 0, '')

    def proc_2_3_3(self, data, flag):
        '''
        SNAC(03,03)     SRV_BUDDYLIST_RIGHTS_REPLY 

        Server replies with this SNAC to SNAC(03,02) - client 
        service parameters request. 
        '''
        log().log("Got (03,03) SRV_BUDDYLIST_RIGHTS_REPLY")

        tlvs = readTLVs(data)
        self.maxBuddies = struct.unpack("!H", tlvs[1])[0]
        self.maxWatchers = struct.unpack("!H", tlvs[2])[0]
        log().log("Max buddies: %d, Max watchers: %d" % (self.maxBuddies, self.maxWatchers))

        '''
        SNAC(04,04)     CLI_ICBM_PARAM_REQ  

        Use this snac to request your icbm parameters from server. 
        Server should reply via SNAC(04,05). 
        You can change them using SNAC(04,02).
        '''
        log().log("Sending (04,04) CLI_ICBM_PARAM_REQ - ICBM service parameters")
        self.sendSNAC(0x04, 0x04, 0, '')

    def sendIdleTime(self, secs = 0):
        '''
        SNAC(01,11)     CLI_SETxIDLExTIME  

        Set idle information. If idle_secs field is 0 then the user 
        isn't idle at all and the server informs all watching clients 
        to remove idletime-string in their tooltip of my uin-item. 
        If idle_secs field is greater then 0 then the user has already 
        been idle for idle_secs number of seconds. The server will 
        automatically keep incrementing this number, so do not repeatedly 
        call with new idle times. 
        '''
        log().log("Sending (01,11) CLI_SETxIDLExTIME")
        self.sendSNAC(0x01, 0x11, 0, struct.pack("!L", secs))

    def proc_2_19_3(self, data, flag):
        '''
        SNAC(13,03)     SRV_SSI_RIGHTS_REPLY 

        Server replies with this SNAC to SNAC(13,02) - 
        client SSI service parameters request. 
        '''
        log().log("Got (13,03) SRV_SSI_RIGHTS_REPLY")

        '''
        SNAC(13,07)     CLI_SSI_ACTIVATE 

        Client should send this snac after login to activate server-side 
        contact. After this snac server start send presense notifications 
        for you.
        '''
        log().log("Sending (13,07) CLI_SSI_ACTIVATE")
        self.sendSNAC(0x13, 0x07, 0, '')

        '''
        SNAC(01,02)     CLI_READY  

        This is the last snac in protocol negotiation sequence. 
        It tells BOS that we are ready to go online. 
        Client must send this snac within 30 seconds after signon, or the 
        connection will be dropped.
        '''
        log().log('Sending (01,02) CLI_READY')
        self.sendClientReady_original()

        # Status
        icqStatus = 0x00
        t = tlv(0x06, struct.pack(">HH", self.statusindicators, icqStatus))

        # DC data
        # DC Internal ip address

        try:
            myip = socket.gethostbyname(socket.gethostname())
            dcData = socket.inet_aton(myip)
        except Exception, exc:
            log().log("Unable to get local host name/address: " + str(exc))
            dcData  = '\x01\x02\x03\x04'

        # DC tcp port
        dcData += '\x00\x00\x00\x00'

        # 0x0000      DC_DISABLED         Direct connection disabled / auth required
        dcData += '\x00'

        # DC protocol version
        dcData += '\x00\x0A'

        # xx xx xx xx       dword       DC auth cookie
        # xx xx xx xx       dword       Web front port
        # 00 00 00 03       dword       Client futures
        dcData += '\x00\x00\x00\x00'
        dcData += '\x00\x00\x00\x00'
        dcData += '\x00\x00\x00\x03'

        # xx xx xx xx       dword       last info update time
        # xx xx xx xx       dword       last ext info update time (i.e. icqphone status)
        # xx xx xx xx       dword       last ext status update time (i.e. phonebook)
        # xx xx             word        unknown
        dcData += '\x00\x00\x00\x00'
        dcData += '\x00\x00\x00\x00'
        dcData += '\x00\x00\x00\x00'
        dcData += '\x00\x00'

        t += tlv(0x0C, dcData)

        '''
        SNAC(01,0E)     CLI_REQ_SELFINFO  

        Client use this SNAC to request own online information (like 
        direct connection info). Server should respond with SNAC(01,0F). 
        '''
        log().log('Sending (01,0E) CLI_REQ_SELFINFO')
        self.sendSNAC(0x01, 0x1e, 0, t)

        self.sendIdleTime(0)

        log().log('{SKIPPED} Getting offline messages...')
        self.getOfflineMessages(self._xmlConfig.get("./Options/Network/ICQ/ICQNumber"))

    def sendClientReady(self):
        '''
        This is Miranda's version of CLI_READY
        '''
        d = ''
        d += '\x00\x01\x00\x04'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x13\x00\x04'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x02\x00\x01'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x03\x00\x01'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x15\x00\x01'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x04\x00\x01'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x06\x00\x01'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x09\x00\x01'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x0A\x00\x01'
        d += '\x01\x10\x08\xE4'
        d += '\x00\x0B\x00\x01'
        d += '\x01\x10\x08\xE4'

        self.sendSNAC(0x01, 0x02, 0, d)

    def sendClientReady_original(self):
        '''
        This is original version of CLI_READY,
        it's replaced with Miranda's one
        '''

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

    def changeStatus(self, status):
        assert type(status) == type('')

        icqStatus = 0

        for k in _userStatusP2:
            if status == _userStatusP2[k]:
                icqStatus = k
                break

        t = tlv(0x06, struct.pack(">HH", self.statusindicators, icqStatus))
        self.sendSNAC(0x01, 0x1e, 0, t)
        
    def proc_2_4_20(self, data, flag):
        '''
        SNAC(04,14)     TYPING_NOTIFICATION     

        This snac used by client and server for mini typing notification (MTN). 
        Basically, when you begin typing something you send a "typing begun" 
        message, then a few seconds later you send a "text typed" message, 
        then after you actually send the message, you send a "no more text 
        has been typed" message. You also send the "typing finished" message 
        if you delete all the stuff you've typed.

        Remote clients know that your client supports MTN because the server 
        appends an empty type 0x000b TLV to all outgoing IMs. You tell 
        the server you want this TLV appended when you send the SNAC(04,02). 
        Just set message flags bit4=1. Send and receive SNACs has the same 
        type=0x14. Here is the known notification types list:

        0x0000 - typing finished sign
        0x0001 - text typed sign
        0x0002 - typing begun sign
        '''
        log().log('Got (04,14) TYPING_NOTIFICATION')

        data = data[8:]
        channel = int(struct.unpack('!H', data[0:2])[0])

        data = data[2:]
        uinLen = int(struct.unpack('!B', data[0])[0])
        uin = str(data[1 : uinLen + 1])

        data = data[1 : uinLen + 1]
        ntype = int(struct.unpack('!H', data[0:2])[0])

        log().log('Got TYPING_NOTIFICATION from %s (not implemented yet)' % uin)

        self.react('Typing notification', uin = uin, ntype = ntype)

    def proc_2_1_33(self, data, flag):
        '''
        SNAC(01,21)     SRV_EXT_STATUS  

        This is an own extended status notification. You'll get this when 
        you have server-stored icon or if you setup iChat "available" message. 
        It's also used to tell the client whether or not it needs to 
        upload an SSI buddy icon. Check for buddy icons info here.

        About icon flags byte. Its purpose is unknown, but i found that 
        bit8=1 is a command to upload icon to server and it is appeared 
        after changing corresponding ssi item.
        '''

        # FIXME:
        log().log('Got (01,21) SRV_EXT_STATUS - extended status (not implemented yet)')

    def proc_2_1_15(self, data, flag):
        '''
        SNAC(01,0F)     SRV_ONLINExINFO  

        Server reply with this SNAC to client SNAC(01,0E) request. 
        Also it sends this snac after client status change. 
        Status change notification SNAC(01,0F) doesn't contain TLV(0x0C), 
        but contain TLV(0x06).
        '''
        log().log('Got (01,0F) SRV_ONLINExINFO')
        uinLen = int(struct.unpack('!B', data[0])[0])
        uin = str(data[1 : uinLen + 1])

        warningLevel, tlvNumber = struct.unpack('!HH', data[uinLen + 1: uinLen + 1 + 4])
        log().log('Got my status report: uin: %s, warning level: %d' %\
            (uin, warningLevel))

        tlvs = readTLVs(data[uinLen + 1 + 4:])
        self.parseSelfStatus(tlvs)

        '''
        SNAC(13,05)     CLI_SSI_CHECKOUT 

        Use this snac to check if your SSI local copy up-to-date (mod-time & 
        items-num match). If not - server will send SSI via SNAC(13,06), 
        overwise you'll receive SNAC(13,0F).
        '''

        log().log("Sending (13,05) CLI_SSI_CHECKOUT - Retrieving server-side contact list")
        data = "\x00\x00\x00\x00\x00\x00"
        self.sendSNAC(0x13, 0x05, 0, data)

        # FIXME:
        #log().log("Retrieving server-side contact list FIRST TIME")
        #self.sendSNAC(0x13, 0x04, 0, '')

#        self.getOfflineMessages()
#        self.sendSNAC(0x13, 0x05, 0, struct.pack('!LH', 0, 0))

    def parseSelfStatus(self, data):
        try:
            self.userClass = int(struct.unpack('!H', data[1])[0])
        except Exception, exc:
            # FIXME: bad way
            log().log("Unable to parse my status: " + str(exc))
        self.parseUserClass()

    def parseUserClass(self, userClass = None):
        if userClass is None:
            userClass = self.userClass
        out = []
        for c in _userClasses:
            if userClass & c: out.append(_userClasses[c])
        log().log("User class: " + ' '.join(out))

    def proc_2_3_1(self, data, flag):
        '''
        SNAC(03,01)     SRV_BLM_ERROR   
        This is an error notification snac.
        '''
        log().log('Got (03,01) SRV_BLM_ERROR')

        errCode = struct.unpack('!H', data[0:2])[0]
        tlvs = readTLVs(data[2:])
        if tlvs.has_key(0x08):
            errSubCode = struct.unpack('!H', tlvs[0x08][0:2])[0]
        else:
            errSubCode = 0
        log().log("SRV_BLM_ERROR: %d/%d" % (errCode, errSubCode))

    def proc_2_19_6(self, data, flag):
        ''' 
        SNAC(13,06)     SRV_SSIxREPLY
        This is the server reply to client roster 
        requests: SNAC(13,04) - Request contact list (first time),
        SNAC(13,05) - Contact list checkout.

        Server can split up the roster in several parts. This is 
        indicated with SNAC flags bit 1 as usual, however the "SSI 
        list last change time" only exists in the last packet. 
        And the "Number of items" field indicates the number of 
        items in the current packet, not the entire list. '''

        log().log('Got (13,06) SRV_SSIxREPLY')

        if __debug__:
            import cPickle
            f = open('userlist.dump', 'wb')
            cPickle.dump(data, f)
            f.close()

        ver = int(struct.unpack('!B', data[0:1])[0])
        assert ver == 0

        nitems = int(struct.unpack('!H', data[1:3])[0])

        # FIXME: problems with SSI list parsing
        if nitems > 500:
            nitems = int(struct.unpack('!H', data[9:11])[0])
            data = data[11:]
        else:
            data = data[3:]

        log().log("Items number: %d" % nitems)

        # FIXME: still have a problems with parsing SSI items
        try:
            for ii in range(0, nitems):
                data = self.parseSSIItem(data)
        except:
            traceback.print_exc(file = sys.stdout)
            #log().log("Exception while parsing SSI items (%s)" % str(msg))
            
        log().log('Current list of groups: %s' % self._groups)

        #log().log('Notify server about our buddy list')
        #self.________sendBuddyList()
        self.sendActivateSSIList()

    def sendActivateSSIList(self):
        log().log('Sending (13,07) CLI_SSI_ACTIVATE - Activate server-side contact')
        self.sendSNAC(0x13, 0x07, 0, '')
        log().log('Activation done (SNAC(13,07)')

    def ___________sendBuddyList(self):
        '''
        SNAC(03,04)     CLI_BUDDYLIST_ADD   

        Use this this to add new buddies to your client-side contact list. 
        You can delete buddies from contact using SNAC(03,05). 
        See also complete snac list for this service here.
        '''
        data = ''
        for b in self._groups.getBuddies():
            data += struct.pack('!H', len(b.uin)) + b.uin
        self.sendSNAC(0x03, 0x04, 0, data)

    def parseSSIBuddy(self, groupID, itemID, name, tlvs):
        '''
        Requires group ID, default user name and list of TLV
        '''

        b = Buddy()
        b.gid = groupID
        b.ids = itemID
        b.uin = name
        b.name = name

        print 'Parsing buddy:', b
        print 'tlvs:', tlvs

        for t in tlvs:
            tmp = "parseSSIItem_%02X" % t
            try:
                func = getattr(self, tmp)
                func(tlvs[t], b)

                if b.name is None:
                    log().log("Buddy name is missing, replacing with UID (%s)" %\
                        name)
                    b.name = name

            except AttributeError, msg:
                log().log("Not fatal exception got: " + str(msg))

                # Bad buddy, mark it as Null, do not add to list
                b = None
                break

        if b is not None:
            try:
                self._groups.getBuddyByUin(b.uin)
            except Exception, msg:
                print msg

                # OK, let's pass new buddy upto gui
                log().log("Got new buddy from SSI list: %s" % b)
                self._groups.addBuddy(groupID, b)

                # ract must be called after groups/buddies list was updated
                self.react("New buddy", buddy = b)

    def getBuddies(self, gid = None, status = None):
        return self._groups.getBuddies(gid = gid, status = status)

    def addBuddyAfterSearch(self, b):
        print 'addBuddyAfterSearch'
        ''' Add buddy after 'search' dialog
        '''
        self._groups.addBuddy(0, b)
        self.react("New buddy", buddy = b)

    def deleteBuddy(self, b):
        self._groups.deleteBuddy(b)
        self.sendSSIDelete(b)

    def getBuddy(self, userName):
        return self._groups.getBuddy(userName)

    def getBuddyByUin(self, uin):
        return self._groups.getBuddyByUin(uin)

    def saveBuddiesList(self, fileName):
        dump2file(fileName, self._groups)

    def loadBuddiesList(self, fileName):
        log().log('Loading buddies list from ' + fileName)
        self._groups = restoreFromFile(fileName)

    def parseSSIItem(self, data):

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
            print "### it's group"
            self._groups.add(groupID, name)
        # FIXME: 25
        elif flagType == 25:
            print "### it's buddy???"
#            if len(name) > 0:
#                import re
#                digit = re.compile('^\d+$')
#                if digit.match(name):
#                    self.parseSSIBuddy(groupID, itemID, name, tlvs)
            pass
        elif flagType == SSI_ITEM_BUDDY:
            print "### it's buddy"
            self.parseSSIBuddy(groupID, itemID, name, tlvs)
        else:
            print "### it's others"
            for t in tlvs:
                tmp = "parseSSIItem_%02X" % t
                try:
                    func = getattr(self, tmp)
                    func(tlvs[t], flagType)
                except AttributeError, msg:
                    log().log("Not fatal exception got: " + str(msg))
     
        data = data[8 + dataLen:]
        return data

    def parseSSIItem_7605(self, t, b):
        '''
        Unknown
        '''
        log().log('Called unknown handler parseSSIItem_7605')

    def parseSSIItem_13C(self, t, b):
        '''
        Unknown
        '''
        log().log('Called unknown handler parseSSIItem_13C')

    def parseSSIItem_6D(self, t, b):
        '''
        Unknown
        '''
        log().log('Called unknown handler parseSSIItem_6D')

    def parseSSIItem_D4(self, t, b):
        '''
         [TLV(0x00D4), itype 0x13, size 04] - TLV for import time 
        item (type 0x0013). Contains timestamp in unix_t format 
        (seconds since 1.1.1970) when the buddylist has been first 
        time uploaded to the server
        '''
        t = struct.unpack('!L', t)[0]
        log().log("Buddy list was first upload to server at %s" % time.asctime(time.localtime(t)))

    def parseSSIItem_13A(self, t, b):
        '''
        [TLV(0x013A), itype 0x00, size XX] - Your buddy locally 
        assigned SMS number.
        '''
        log().log("Client's SMS number: %s" % str(t))

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
        log().log("Master group IDs: " + coldump(t))

    def parseSSIItem_5D47(self, t, flag):
        ''' Unknown '''
        log().log('Called unknown handler parseSSIItem_5D47')

    def proc_2_3_12(self, data, flag):
        ''' Server send this when user from your contact list goes 
        offline. See also additional information about online userinfo block.
        '''

        uinLen = int(struct.unpack('!B', data[0])[0]) 
        uin = data[1 : uinLen + 1]
        log().log("User '%s' is offline" % uin)
        log().log("UIN length: %d, UIN: %s" % (uinLen, uin))

        data = data[1 + uinLen:]

        warningLevel = int(struct.unpack('!H', data[0:2])[0]) 
        ntlv = int(struct.unpack('!H', data[2:4])[0]) 
        log().log("Warning level: %d. number of TLV: %d" % (warningLevel, ntlv))

        tlvs = readTLVs(data[4:])
        userClass = int(struct.unpack('!H', tlvs[0x01])[0])

        self._groups.getBuddyByUin(uin).status = 'offline'
        b = self._groups.getBuddyByUin(uin)

        self.react("Buddy status changed", buddy = b)

    def proc_2_11_2(self, data, flag):
        '''
        SNAC(0B,02)     SRV_SET_MINxREPORTxINTERVAL  

        Server send this to client after login. This snac contain minimum 
        stats report interval value. Client should send stats report 
        every 1200 hours (default value). 
        See HKLM\SOFTWARE\Mirabilis\ICQ\Owners\6218895\Prefs\Stats in your 
        registry for ICQ stats information (don't forget to change uin 
        number in the path)
        '''
        log().log('Got (0B,02) SRV_SET_MINxREPORTxINTERVAL')
        hours = int(struct.unpack('!H', data[0:2])[0]) 
        log().log("Server set minimum stats report interval: %d hours" % hours)

    def proc_2_3_11(self, data, flag):
        ''' 
        SNAC(03,0B)     SRV_USER_ONLINE  
        Server sends this snac when user from your contact list 
        goes online. Also you'll receive this snac on user status 
        change (in this case snac doesn't contain TLV(0xC)). 
        See also additional information about online userinfo block. '''

        log().log('Got (03,0B) SRV_USER_ONLINE')

        uinLen = int(struct.unpack('!B', data[0])[0]) 
        uin = data[1 : uinLen + 1]
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
            log().log("Client uses protocol v%d" % dcProtocolVersion)

            assert clientFutures == 0x03

            lastInfoUpdate = int(struct.unpack('!L', dc[14 : 18])[0])
            lastExtInfoUpdate = int(struct.unpack('!L', dc[18 : 22])[0])
            lastExtStatusUpdate = int(struct.unpack('!L', dc[22 : 26])[0])

#           What's format for this time? Fails.
#            print "lastInfoUpdate: %s, lastExtInfoUpdate: %s, lastExtStatusUpdate: %s" % \
#                (time.asctime(time.localtime(lastInfoUpdate)), time.asctime(time.localtime(lastExtInfoUpdate)), time.asctime(time.localtime(lastExtStatusUpdate)))

            junk = int(struct.unpack('!H', dc[26 : 28])[0])
        except Exception, e:
            log().log("Exception while parsing DC info: %s" % str(e))

        # TLV.Type(0x0A) - external ip address
        externalIP = "0:0:0:0"
        try:
            externalIP = socket.inet_ntoa(tlvs[0x0a][0 : 4])
        except Exception, msg:
            pass # FIXME
        log().log("External IP: %s" % externalIP)

        print tlvs

        # TLV.Type(0x06) - user status
        if tlvs.has_key(0x06):
            userStatus = tlvs[0x06][0 : 4]
            log().log("User status: %s" % self._parseUserStatus(userStatus))
        else:
            log().log("Unable to get user status, setting default to online")
            userStatus = '\x00\x00\x00\x00' # online

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

        status = self.splitUserStatus(userStatus)
        textStatus = self.decodeOnlineStatus(status[1])

        self._groups.getBuddyByUin(uin).status = textStatus
        b = self._groups.getBuddyByUin(uin)

        self.react("Buddy status changed", buddy = b)

    def setBuddyNick(self, b, nick = None):
        assert isinstance(b, Buddy)

        if nick is None:
            if hasattr(b, 'nick') and b.nick is not None:
                nick = b.nick
            else:
                return
        self._groups.setBuddyNick(b, nick)

    def decodeOnlineStatus(self, status):
        '''
        Return textual representation of status, e.g. 'online', 'na' etc.
        '''

        print "decodeOnlineStatus got status: ", status

        d = _userStatusP2.keys()
        d.reverse()

        for s in d:
            if s & status:
                return _userStatusP2[s]
                print "decodeOnlineStatus return status: ", _userStatusP2[s]

        print "decodeOnlineStatus return status: ", _userStatusP2[0]
        return _userStatusP2[0]

    def splitUserStatus(self, status):
        '''
        ICQ service presence notifications use user status field which 
        consist of two parts. First is a various flags (birthday flag, 
        webaware flag, etc). Second is a user status (online, away, 
        busy, etc) flags. Each part is a two bytes long.
        '''
        return struct.unpack('!HH', status)

    def _parseUserStatus(self, status):
        p1, p2 = self.splitUserStatus(status)
        st = []

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

    def proc_2_19_8(self, data, flag):
        '''
        SNAC(13,08)     CLI_SSIxADD 

        Client use this to add new items to server-side info. 
        Server should reply via SNAC(13,0E).     
        '''
        log().log('Got (13,08) CLI_SSIxADD')
 
    def proc_2_19_21(self, data, flag):
        '''
        SNAC(13,15)     SRV_SSI_FUTURExAUTHxGRANTED 

        You'll receive this when somebody grants future authorization to you. 
        You can use SNAC(13,14) to send such authorization grant.
        '''
        log().log('Got SNAC(13,15) SRV_SSI_FUTURExAUTHxGRANTED ')

        uinLen = int(struct.unpack('!B', data[0])[0]) 
        uin = data[1 : uinLen + 1]
        log().log("Authorization granted by '%s'" % uin)

        data = data[uinLen + 1:]
        reasonLen = int(struct.unpack('!B', data[0])[0]) 
        reason = data[1 : reasonLen + 1]
        log().log("Authorization reason '%s'" % reason)

        self.react("Authorization granted", uin = uin, reason = reason)
 
    def proc_2_19_10(self, data, flag):
        '''
        SNAC(13,0A)     CLI_SSIxDELETE 

        Client use this to delete items from server-side info. 
        Server should reply via SNAC(13,0E). 
        '''
        log().log('Got (13,0A) CLI_SSIxDELETE')

    def proc_2_19_15(self, data, flag):
        '''
        SNAC(13,0F)     SRV_SSI_UPxTOxDATE  

        Server send this snac as reply for SNAC(13,05) when server-stored 
        information has the same modification date and items number.
        '''
        timestamp = struct.unpack('!L', data[:4])
        items = struct.unpack('!H', data[4:6])
        print timestamp, items
        log().log("Warning: proc_2_19_15 (SRV_SSI_UPxTOxDATE) not implemented")

        #self.sendActivateSSIList()

    def sendAuthorizationReply(self, b, flag, reason = None):
        '''
        Approve/reject authentification request which we've got from user
        '''

        if flag: flag = 1
        else: flag = 0

        if reason is None:
            reason = _default_reject_reason

        data = struct.pack('!B', len(b.uin)) + b.uin
        data += struct.pack('!B', flag)
        data += struct.pack('!B', len(reason)) + reason

        log().log("Sending authorization reponse (%d) to %s" % (flag, b.uin))
        self.sendSNAC(0x13, 0x0A, 0, data)

    def proc_2_4_1(self, data, flag):
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
        log().log('Got (04,01) SRV_ICBM_ERROR')
        errorCode = int(struct.unpack('!H', data[0:2])[0])
        tlvs = readTLVs(data[2:])

        subErrorCode = 0
        try:
            subErrorCode = int(struct.unpack('!H', tlvs[0x08])[0])
        except KeyError, msg:
            log().log("No error subcode found")

        log().log("Can't send your message to recipient (%d, %d) (%s)" %\
            (errorCode, subErrorCode, _msg_error_codes[errorCode]))

    def proc_2_4_10(self, data, flag):
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

        log().log("Got (04,0A) SRV_MISSED_MESSAGE")

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

    def proc_2_4_7(self, data, flag):
        '''
        SNAC(04,07)     SRV_CLIENT_ICBM 

        You'll receive this snac when another client send you a message thru 
        server. Within the ICBM (Inter-Client Basic Message) types, a channel 
        is defined. Each channel represents a different kind of message.

        Channel 1 is used for simple plain text messages. 
        Channel 2 is used for complex messages (rtf, utf8) and 
        negotiating "rendezvous". These transactions end in something more 
        complex happening, such as a chat invitation, or a file transfer. 
        Channel 4 is used for various ICQ messages. Examples are normal 
        messages, URLs, and old-style authorization.
        '''

        log().log('Got (04,07) SRV_CLIENT_ICBM')

        cookie = data[0:7]
        messageChannel = int(struct.unpack('!H', data[8:10])[0])
        snameLen = int(struct.unpack('!B', data[10])[0])
        sname = data[11:11 + snameLen]
        data = data[11 + snameLen:]

        log().log('Got message from %s, channel: %d, from: %s' % 
            (sname, messageChannel, sname))

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
        mtype, msg = func(tlvs)

        # FIXME: will throw exceptino when buddy is not in current list
        try:
            b = self._groups.getBuddyByUin(sname)
        except NotFound, exc:
            log().log("Looks like new user: " + str(exc))

            b = Buddy()
            b.uin = sname
            b.name = sname

        if mtype == MTYPE_AUTHREQ:
            log().log("Got authentification request message")
            self.react("Authentification request", buddy = b)
        else:
            m = messageFactory("icq",
                b.name, b.uin, msg, HistoryDirection.Incoming)

            self.react("Incoming message", buddy = b, message = m)

#        try:
#            if msg == 'winamp':
#                from thirdparty.WinampInfo import WinampInfo
#                w = WinampInfo()
#                reply = "Andrey Sidorenko's WinAmp status:"  + " "
#                reply += w.getPlayingStatus() + " "
#                reply += w.getCurrentTrackName() + " "
#                print reply
#                msg = ICQMessage(sname, sname, reply)
#                self.sendMessage(msg)
#       except Exception, msg:
#            print msg
#            pass

    # 13 1C / 19 28

    def proc_2_19_28(self, data, flag):
        ''' 
        SNAC(13,1C)     SRV_SSI_YOUxWERExADDED 

        Server send this snac to clients, that announced the use of 
        family 0x13 in SNAC(01,17). This is the "you-were-added" message 
        meaning that somebody (snac contain his/her screenname) added you to 
        his/her roster.
        '''
        log().log('Got (13,1C) SRV_SSI_YOUxWERExADDED')
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

        return (mtype, msg)

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
        return (0, msg)

    def proc_2_4_12(self, data, flag):
        '''
        SNAC(04,0C)     SRV_MSG_ACK  

        This is the server ack for client message sent via SNAC(04,06). 
        Server send it only if client requested it via empty TLV(3) in 
        message snac. This ack mean that server accepted message for 
        delivery.
        '''
        print ashex(data)
        channel = int(struct.unpack('!H', data[8:10])[0])

        uinLen = int(struct.unpack('!B', data[10:11])[0])
        uin = data[11 : 11 + uinLen]
        log().log("Server accepted message for delivery (%s)" % uin)

    def proc_2_2_3(self, data, flag):
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

    def getFullUserInfo(self, ownerUin, uin):
        '''
        Client full userinfo request. Last reply snac flag bit1=0, 
        other reply packets have flags bit1=1 to inform client that 
        more data follows. Server should respond with following SNACs:

        SNAC(15,03)/07DA/00C8, SNAC(15,03)/07DA/00DC,
        SNAC(15,03)/07DA/00EB, SNAC(15,03)/07DA/010E,
        SNAC(15,03)/07DA/00D2, SNAC(15,03)/07DA/00E6,
        SNAC(15,03)/07DA/00F0, SNAC(15,03)/07DA/00FA 
        '''
        data = struct.pack('<L', int(ownerUin))
        data += "\xd0\x07\x02\x00\xb2\x04"
        data += struct.pack('<L', int(uin))

        data = struct.pack('<H', len(data)) + data

        if self._currentUser == None:
            self._currentUser = Buddy()
            self._currentUser.uin = uin

        log().log("Sending full user info request for '%s'" % str(uin))
        self.sendSNAC(0x15, 0x02, 0, tlv(0x01, data))

    def addSSIItem(self):
        '''
        SNAC(13,08)     CLI_SSIxADD     

        Client use this to add new items to server-side info. 
        Server should reply via SNAC(13,0E).

        xx xx      word        Length of the item name 
        xx ..      string      Item name string    
        xx xx      word        Group ID#   
        xx xx      word        Item ID#    
        xx xx      word        Type of item flag (see list bellow) 
        xx xx      word        Length of the additional data   

        xx xx      word        TLV.Type (TLV #1)   
        xx xx      word        TLV.Length  
        .. ..      xxxx        TLV.Value
                   ....
        '''
        pass

    def addBuddyToList(self, buddies):
        '''
        SNAC(03,04)     CLI_BUDDYLIST_ADD   

        Use this this to add new buddies to your client-side 
        contact list. You can delete buddies from contact using 
        SNAC(03,05). See also complete snac list for this service here.
        '''

        if type(buddies) != type([]):
            buddies = [buddies]

        log().log('Called add user to contact list (CLI_BUDDYLIST_ADD)')

        out = ''
        for b in buddies:
            out += struct.pack('!H', len(b.uin)) + b.uin

        self.sendSNAC(0x03, 0x04, 0, out)

    def proc_2_21_3_41(self, data, flag):
        '''
        SNAC(15,03)/0041    SRV_OFFLINE_MESSAGE  

        This is the server response to cli_offline_msgs_req SNAC(15,02)/003C. 
        This snac contain single offline message that was sent by another 
        user and buffered by server when client was offline.         
        '''
        log().log('SNAC(15,03)/0041 SRV_OFFLINE_MESSAGE')

        tlvs = readTLVs(data)
        d = tlvs[1]

        dsize, targetUin, dataType, seqNum = struct.unpack("<HLHH", d[:10])
        assert dataType == 0x41
        assert seqNum == 0x02

        d = d[10:]
        ownerUin = str(int(struct.unpack("<L", d[:4])[0]))
        year = struct.unpack("<H", d[4:6])[0]
        month, day, hour, minute, mtype, mflags, mlen = struct.unpack("!ccccccH", d[6:6+8])
        month, day, hour, minute, mtype, mflags = map(ord, [month, day, hour, minute, mtype, mflags])

        # FIXME: wrong handling of TZ
        if time.localtime()[-1] != 0:
            td = datetime.timedelta(hours = abs(time.altzone / 60 / 60) - time.localtime()[-1])

            if time.altzone < 0:
                dt = datetime.datetime(year, month, day, hour, minute) + td
            elif time.altzone > 0:
                dt = datetime.datetime(year, month, day, hour, minute) - td
        else:
            dt = datetime.datetime(year, month, day, hour, minute)
        log().log("Message was send at: " + dt.ctime())

        text = d[8 + 6:-1]
        log().log("Message text:\n" + ashex(text))

        msg = messageFactory("icq", ownerUin, ownerUin, text, HistoryDirection.Incoming)
        self._offlineMessageQueue.append(msg)

    def proc_2_21_3_42(self, data, flag):
        '''
        SNAC(15,03)/0042    SRV_END_OF_OFFLINE_MSGS  

        This is the last SNAC in server response to cli_offline_msgs_req 
        SNAC(15,02)/003C. It doesn't contain message - it is only 
        end_of_sequence marker. 
        '''
        log().log('Got SNAC(15,03)/0042 SRV_END_OF_OFFLINE_MSGS')

        tlvs = readTLVs(data)
        d = tlvs[1]

        dsize, ownerUin, dataType, seqNum = struct.unpack("<HLHH", d[:10])
        assert dataType == 0x42
        assert seqNum == 0x02

        self.react('Offline messages', queue = self._offlineMessageQueue)

    def proc_2_21_3(self, data, flag):
        '''
        SNAC(15,03)     SRV_META_REPLY  

        This is the server response to client meta request SNAC(15,02). 
        '''
        tlvs = readTLVs(data)
        d = tlvs[1]

        # First we should distinguish two different types of messsages,
        # is it SNAC(15,03)/0041 SRV_OFFLINE_MESSAGE or SRV_META_REPLY

        dsize, ownerUin, dataType, seqNum = struct.unpack("<HLHH", d[:10])
        if dataType == 0x41 and seqNum == 0x02:
            # Got SRV_OFFLINE_MESSAGE
            self.proc_2_21_3_41(data, flag)
            return
        elif dataType == 0x42 and seqNum == 0x02:
            # Got SRV_END_OF_OFFLINE_MSGS
            self.proc_2_21_3_42(data, flag)
            return

        log().log('Got (15,03) SRV_META_REPLY')

        # Then parse the rest of data
        dataSubType = struct.unpack("<H", d[10:12])

        dataTypeX = "%04X" % dataType
        dataSubTypeX = "%04X" % dataSubType

        tmp = "userFound_%s_%s" % (dataTypeX, dataSubTypeX)

        #dump2file(tmp, d[12:])

        try:
            func = getattr(self, tmp)
            func(d[12:])
        except Exception, exc:
            log().log("Exception while parsing user details: " + str(exc))

        if flag == 0:
            log().log("It was last META information packet")
            self.react('Last meta', buddy = self._currentUser)
            self._currentUser = None

    def userFound_07DA_00C8(self, data):
        '''
        SNAC(15,03)/07DA/00C8   META_BASIC_USERINFO 

        Basic user information packet. If success byte doesn't equal 0x0A - it is last SNAC byte. 
        '''

        log().log('Got META_BASIC_USERINFO packet')

        if self._currentUser == None:
            self._currentUser = Buddy()

        d = data
        assert d[0] == '\x0a'

        vals = ['nick', 'first', 'last', 'email', 'city', 'state', 'phone',
            'fax', 'address', 'cell', 'zip']

        rest =['coutry_code', 'gmt_offset', 'authorization_flag',
            'webaware_flag', 'dc_permission', 'publish_primary_email_flag']

        d = d[1:]

        self._parseVals(vals, d)
        print self._currentUser

    def userFound_07DA_00DC(self, data):
        '''
        SNAC(15,03)/07DA/00DC   META_MORE_USERINFO 

        More user information packet. If success byte doesn't equal 0x0A - it is 
        last SNAC byte. This snac contain some data not setable/viewable in current 
        ICQ clients (except ICQLite and ICQ2003b), but you can change it thru your 
        whitepage on wwp.icq.com. ICQLite (up to build 1150) doesn't use "marital 
        status" field too. 
        '''

        log().log('Got META_MORE_USERINFO packet')

        if self._currentUser == None:
            self._currentUser = Buddy()

        d = data
        assert d[0] == '\x0a'

        vals = [('age',), ('gender', ''), 'homepage_address', 
            ('birth_year',), ('birth_month', ''), ('birth_day', ''), 
            ('speaking_language_1', ''), ('speaking_language_2', ''), 
            ('speaking_language_3', ''), ('unknown'), 'original_from_city',
            'original_from_state', ('original_from_country_code',), ('timezone', '')
        ]

        d = d[1:]

        self._parseVals(vals, d)
        print self._currentUser


    def userFound_07DA_00D2(self, data):
        '''
        SNAC(15,03)/07DA/00D2   META_WORK_USERINFO 

        Work user information packet. If success byte doesn't equal 0x0A - it is last SNAC byte. 
        '''

        log().log('Got META_WORK_USERINFO packet')

        if self._currentUser == None:
            self._currentUser = Buddy()

        d = data
        assert d[0] == '\x0a'

        vals = ['work_city', 'work_state', 'work_phone', 'work_fax',
            'work_address', 'work_zip', ('work_country_code',), 'work_company', 
            'work_department', 'work_position', ('work_occupation_code',),
            'work_webpage' ]

        d = d[1:]

        self._parseVals(vals, d)
        print self._currentUser

    def userFound_07DA_00E6(self, data):
        '''
        SNAC(15,03)/07DA/00E6   META_NOTES_USERINFO 

        Notes user information packet. If success byte doesn't 
        equal 0x0A - it is last SNAC byte. 
        '''

        log().log('Got META_NOTES_USERINFO packet')

        vals = [ 'notes' ]

        d = data
        d = d[1:]

        self._parseVals(vals, d)
        print self._currentUser

    def userFound_07DA_00EB(self, data):
        '''
        SNAC(15,03)/07DA/00EB   META_EMAIL_USERINFO 

        Extended email user information packet. If success byte doesn't 
        equal 0x0A - it is last SNAC byte. 
        '''

        log().log('Got META_EMAIL_USERINFO packet')

        d = data
        d = d[1:]

        nemail, d = parseByteLE(d)
        nemail = int(nemail)

        if nemail != 0:
            for ii in range(nemail):
                value, d = parseAsciiz(d)

            pemail_flag, d = parseByteLE(d)
            emailn, d = parseAsciiz(d)
            print emailn

        print self._currentUser

    def userFound_07DA_00F0(self, data):
        '''
        SNAC(15,03)/07DA/00F0   META_INTERESTS_USERINFO 

        Interests email user information packet. If success 
        byte doesn't equal 0x0A - it is last SNAC byte. 
        '''

        log().log('Got META_INTERESTS_USERINFO packet')

        d = data
        assert d[0] == '\x0a'

        d = d[1:]

        nelem, d = parseByteLE(d)

        for ii in range(int(nelem) - 1):
            interest_code, d = parseByteLE(d)
            interest, d = parseAsciiz(d)
            print interest_code, interest_code

    def userFound_07DA_00FA(self, data):
        '''
        SNAC(15,03)/07DA/00FA   META_AFFILATIONS_USERINFO 

        Past/Affilations email user information packet. 
        If success byte doesn't equal 0x0A - it is last SNAC byte. 
        '''

        log().log('Got META_AFFILATIONS_USERINFO packet')

        d = data
        if d[0] != '\x0a':
            log().log('Warning: Mailformed META_AFFILATIONS_USERINFO packet')
            return

        d = d[1:]

        nelem, d = parseByteLE(d)

        for ii in range(int(nelem) - 1):
            past_category_code, d = parseWordLE(d)
            past_keyword, d = parseAsciiz(d)
            print past_category_code, past_keyword

        nelem, d = parseByteLE(d)

        for ii in range(int(nelem) - 1):
            aff_category_code, d = parseWordLE(d)
            aff_keyword, d = parseAsciiz(d)
            print aff_category_code, aff_keyword

    def userFound_07DA_010E(self, data):
        '''
        SNAC(15,03)/07DA/010E   META_HPAGECAT_USERINFO 

        Homepage category user information packet. If success byte 
        doesn't equal 0x0A - it is last SNAC byte. 
        '''

        log().log('Got META_HPAGECAT_USERINFO packet')

        d = data
        assert d[0] == '\x0a'

        d = d[1:]

        enabled_flag, d = parseByteLE(d)
        enabled_flag = int(enabled_flag)

        if enabled_flag != 0:
            homepage_category, d = parseWordLE(d)
            homepage_keywords, d = parseAsciiz(d)
            print homepage_category, homepage_keywords

    def _parseVals(self, vals, d):
        b = self._currentUser

        for v in vals:
            if type(v) == type(()):
                if len(v) == 1:
                    value, d = parseWordLE(d)
                else:
                    value, d = parseByteLE(d)
                exec("self._currentUser.%s = %d" % (v[0], value))
            else:
                value, d = parseAsciiz(d)
                exec("self._currentUser.%s = '''%s'''" % (v, value))

    def userFound_07DA_01A4(self, data):
        '''
        SNAC(15,03)/07DA/01A4   SRV_USER_FOUND  

        This is the server response to search request. 
        This is not last search packet. SNAC flags bit1 allways=1. 
        Server sends last search found record via SNAC(15,03)/07DA/01AE. 
        Success byte allways = 0xA (SEARCH_SUCCESS). 
        '''
        self.userFound_07DA_019A(data, skipUserLeft = True)

    def userFound_07DA_01AE(self, data):
        '''
        SNAC(15,03)/07DA/01AE   SRV_LAST_USER_FOUND  

        This is the server response to search request. 
        This is the last search packet. SNAC flags bit1 allways=0. 
        Server sends non-last search found records via SNAC(15,03)/07DA/01A4. 
        '''
        self.userFound_07DA_019A(data)

    def userFound_07DA_019A(self, data, skipUserLeft = False):
        '''
        SNAC(15,03)/07DA/01AE   SRV_LAST_USER_FOUND     

        This is the server response to search request. This is the last 
        search packet. SNAC flags bit1 allways=0. Server sends non-last 
        search found records via SNAC(15,03)/07DA/01A4.
        '''

        print coldump(data)

        successByte  = data[:1]
        dsize = struct.unpack("<H", data[1:3])
        uin = str(struct.unpack("<L", data[3:7])[0])
        data = data[7:]

        nickLen = int(struct.unpack('<H', data[0:2])[0])
        nick = str(data[2 : nickLen + 1])
        data = data[nickLen + 2:]

        firstLen = int(struct.unpack('<H', data[0:2])[0])
        first = str(data[2 : firstLen + 1])
        data = data[firstLen + 2:]

        lastLen = int(struct.unpack('<H', data[0:2])[0])
        last = str(data[2 : lastLen + 1])
        data = data[lastLen + 2:]

        emailLen = int(struct.unpack('<H', data[0:2])[0])
        email = str(data[2 : emailLen + 1])
        data = data[emailLen + 2:]

        authFlag = data[:1]
        status = struct.unpack("<H", data[1:3])[0]
        data = data[3:]

        gender = data[:1]

        age = int(struct.unpack("<H", data[0:2])[0])
        data = data[2:]


        log().log("Nick: %s, First: %s, Last: %s, E-mail: %s, Age: %d" %\
            (nick, first, last, email, age))

        try:
            if not skipUserLeft:
                usersLeft = struct.unpack("<L", data)[0]
                log().log("User left: %d" % usersLeft)
        except struct.error, exc:
            log().log("Unable to get count of users left")

        b = Buddy()
        b.uin = uin
        b.name = nick
        b.first = first
        b.last = last
        b.email = email
        b.gender = gender
        b.age = age

        self.react("Results", buddy = b)

    def proc_2_3_10(self, data, flag):
        '''
        SNAC(03,0A)     SRV_NOTIFICATION_REJECTED  

        Sometimes server send this as reply for SNAC(03,04) entry. 
        This mean that it can't send notification about this user for 
        some reason. The reason is unknown. 
        '''
        # FIXME:
        log().log('Got (03,0A) SRV_NOTIFICATION_REJECTED')

    def proc_4_9_2(self, data, flag):
        '''
        You have been disconnected from the ICQ network because you 
        logged on from another location using the same ICQ number. 
        '''
        log().log('Got (4,9,2) - You have been disconnected')
        self.disconnect()
        log().log("You have been disconnected from the ICQ network because you logged on from another location using the same ICQ number.")

    def proc_1_0_0(self, data, flag):
        log().log("Logging in...")

    def CLI_FIND_BY_UIN2(self):
        # FIMXE: wtf?
        log().log("CLI_FIND_BY_UIN2")
        tlvs = tlv(0x01, struct.pack())

    def CLI_WHITE_PAGES_SEARCH2(self):
        # FIMXE: wtf?
        log().log("CLI_WHITE_PAGES_SEARCH2")

    def getOfflineMessages(self, uin):
        ''' 
        Client sends this SNAC when wants to retrieve messages 
        that was sent by another user and buffered by server during 
        client was offline. 
        '''
        # FIXME: 15/02 - wrong type for offline message retrieveing
        tlvs = tlv(0x01, '\x08\x00' + struct.pack("<L", int(uin)) + '\x3c\x00\x02\x00')
        self.sendSNAC(0x15, 0x02, 0, tlvs)

    def sendHelloServer(self):
        # First we need to disconnect, if we're connected

        try:
            log().log("Trying to disconnect before registration...")
            self.disconnect()
        except Exception, exc:
            log().log("Got exception while disconnection: " + str(exc))

        self._host = 'ibucp-vip-d.blue.aol.com'
        self._port = 5190
        self.connect(self._host, self._port)
        #self.connect(self._host, self._port)
        log().log('Sending HELLO to server (%s:%d)...' % (self._host, self._port))

        buf = self.read()
        log().packetin(buf)

        self.sendCliHello()
        time.sleep(0.1)

        self.registrationImageRequest()
        time.sleep(0.1)

        buf = self.read()
        log().packetin(buf)

        self._dispatchOnce(buf)

    def _dispatchOnce(self, buf):
        ch, b, c = self.readFLAP(buf)
        snac = self.readSNAC(c)

        print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
        print 'for this snac: ', snac

        tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
        flag1, flag2 = snac[2], snac[3]
        func = getattr(self, tmp)

        func(snac[5], flag2)

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

        #i=snac[5].find("\000")
        #print i
        #snac[5]=snac[5][i:]

        # FIXME: why we need to skip first char?
        snac[5]=snac[5][1:]

        tlvs=readTLVs(snac[5])
        log().log(tlvs)

        import cPickle
        f = open('chunk.dump', 'wb')
        cPickle.dump(buf, f)
        f.close()

        if tlvs.has_key(TLV_ErrorCode):
            xerror = explainError(tlvs[TLV_ErrorCode])
            log().log("Error: " + xerror)
            raise Exception(xerror)

        server = ''
        if tlvs.has_key(TLV_Redirect):
            server = tlvs[TLV_Redirect]
            log().log("Redirecting to: " + server)

        self._sock.disconnect()

        print tlvs.keys(), tlvs.values()

        # Was:
        #self._host, self._port = server.split(':')
        #self._port = int(self._port)

        # Now
        host, port = server.split(':')
        port = int(port)

        self.connect(host, port)

        buf = self.read()
        log().packetin(buf)

        self.sendFLAP(0x01, '\000\000\000\001' + tlv(0x06, tlvs[TLV_Cookie]))

        log().log('Post login, getting meta information about ourselfs')

        myUin = self._xmlConfig.get("./Options/Network/ICQ/ICQNumber")
        self._currentUser = Buddy()
        self._currentUser.uin = myUin

        uin = struct.pack('<L', int(myUin))
        data = uin
        data += '\xd0\x07\x02\x00\xd0\x04' + uin
        data = struct.pack('<H', len(data)) + data

        tlvs = tlv(1, data)
        self.sendSNAC(0x15, 0x02, 0, tlvs)

        log().log('Login done')
        self.react('Login done')

        if mainLoop:
            log().log('Going to main loop')
            self.mainLoop()

    def mainLoop(self):
        # self.keepGoing must be externally created or defined in derived class
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

    def proc_2_19_14(self, data, flag):
        '''
        SNAC(13,0E)     SRV_SSIxMODxACK     

        This SNAC is an ack sent by the server when adding a buddy, 
        deleting a buddy, or otherwise modifying a group. 
        See also snac list for SSI service here. This snac contain flag. 
        Here is the list of its known values:

          0x0000      No errors (success)   
          0x0002      Item you want to modify not found in list 
          0x0003      Item you want to add allready exists  
          0x000A      Error adding item (invalid id, allready in list, 
                      invalid data)    
          0x000C      Can't add item. Limit for this type of items exceeded 
          0x000D      Trying to add ICQ contact to an AIM list  
          0x000E      Can't add this contact because it requires authorization
        '''

        log().log('Got (13,0E) SRV_SSIxMODxACK - server response while modifying SSI data')

        while len(data) >= 2:
            code = struct.unpack('!H', data[0:2])
            print 'CODE:', code, ashex(data[0:2])
            data = data[2:]

    def sendAuthorizationRequest(self, b):
        '''
        SNAC(13,18)     CLI_SSI_SEND_AUTHxREQUEST 

        Client use this snac to send authorization request. 
        It contain screen name (uin) of the user and reason string. 
        After that you may receive SNAC(13,1B) - authorization reply.
        '''
        _authReason = 'Please authorize me'
        data = struct.pack('!B', len(b.uin)) + b.uin
        data += struct.pack('!H', len(_authReason)) + _authReason
        data += '\x00\x00'

        log().log('Sending (13,18) CLI_SSI_SEND_AUTHxREQUEST')
        self.sendSNAC(0x13, 0x18, 0, data)

    def proc_2_19_18(self, data, flag):
        '''
        SNAC(13,12)     CLI_SSI_EDIT_END 

        This snac used after SSI modification to commit transaction 
        started by SNAC(13,11). See also snac list for SSI service here. 
        '''
        print 'Got 19/18 reply'
        print coldump(flag)
        print coldump(data)

    def proc_2_19_9(self, data, flag):
        '''
        SNAC(13,09)     CLI_SSIxUPDATE 

        This can be used to modify either the name or additional data for 
        any items that are already in your server-stored information. 
        It is most commonly used after adding or removing a buddy: you 
        should either add or remove the buddy ID# from the 
        type 0x00c9 TLV in the additional data of the parent group, 
        and then send this SNAC containing the modified data. 
        Server should reply via SNAC(13,0E). 
        '''
        print 'Got 19/9 reply'
        print coldump(flag)
        print coldump(data)

    def proc_2_19_17(self, data, flag):
        '''
        Strange - why we got it from server?

        SNAC(13,11)     CLI_SSI_EDIT_BEGIN 

        Use this before server side information (SSI) modification. 
        Also you should send SNAC(13,12) after SSI modification. 
        You could also use "import" transaction mode to add contacts 
        requiring authorization. Just add 0x00010000 to snac data to 
        start import transaction. See also snac list for SSI service here. 
        '''
        print 'Got 19/17 reply'
        print coldump(flag)
        print coldump(data)

    def sendSSIAdd(self, b, awaitingAuth = True):
        '''
        SNAC(03,04)     CLI_BUDDYLIST_ADD   

        Use this this to add new buddies to your client-side contact list. 
        You can delete buddies from contact using SNAC(03,05). 
        See also complete snac list for this service here.
        '''
        log().log('Sending (03,04) CLI_BUDDYLIST_ADD')
        #data = '\x2a\x02\x28\x8d\x00\x1d\x00\x13-00\x08\x00\x00\x00\x08\x00\x08\x00\x09\x32\x36\x34\x30\x32\x35-33\x32\x34\x54\x30\x49\x2c\x00\x00\x00\x00'
        #self.send(data)
        #return

        data = ''
        data += struct.pack('!H', len(b.uin))
        data += b.uin

        gid = 0
        itemid = 99
        itemFlag = 0x0000
        data += struct.pack('!H', gid)

        sitemid = struct.pack('!H', itemid)
        print '>>>', type(data), type(sitemid), coldump(sitemid)
        data = str(data)
        data += sitemid

        data += struct.pack('!H', itemFlag)

        # You can't add buddy that requires authorization without permission. 
        # You can add it only with TLV(0x0066) as a buddy record awaiting 
        # authorization.

        data2 = ''
        # FIXME: doesn't work
        #if awaitingAuth:
        #    data2 += tlv(0x0066, '')
        data2 += tlv(0x0066, '')

        # Length of additional data
        dataLen = len(data2)
        print 'dataLen', dataLen
        data += struct.pack('!H', dataLen)
        data += data2

        log().log("Adding user '%s' to server-side contact list" % b.uin)
        self.sendSNAC(0x13, 0x08, 0, data)

    def sendSSIDelete(self, b):
        '''
        SNAC(13,0A)     CLI_SSIxDELETE  

        Client use this to delete items from server-side info. 
        Server should reply via SNAC(13,0E).
        '''
        print b
        data = ''
        data += struct.pack('!H', len(b.uin))
        data += b.uin

        gid = b.gid
        itemid = b.ids
        itemFlag = 0x0000
        data += struct.pack('!H', gid)

        sitemid = struct.pack('!H', itemid)
        print '>>>', type(data), type(sitemid), coldump(sitemid)
        data = str(data)
        data += sitemid

        data += struct.pack('!H', itemFlag)

        # You can't add buddy that requires authorization without permission. 
        # You can add it only with TLV(0x0066) as a buddy record awaiting 
        # authorization.

        data2 = ''
        # FIXME: doesn't work
        #if awaitingAuth:
        #    data2 += tlv(0x0066, '')

        # Length of additional data
        dataLen = len(data2)
        data += struct.pack('!H', dataLen)
        data += data2

        log().log("Delete ((13,0A) CLI_SSIxDELETE  ) user '%s' from server-side contact list" % b.uin)
        self.sendSNAC(0x13, 0x0a, 0, data)

    def sendSSIEditBegin(self, isImport = False):
        '''
        SNAC(13,11)     CLI_SSI_EDIT_BEGIN

        Use this before server side information (SSI) modification.
        Also you should send SNAC(13,12) after SSI modification.
        You could also use "import" transaction mode to add contacts
        requiring authorization. Just add 0x00010000 to snac data to start
        import transaction. See also snac list for SSI service here.
        '''
        data = ''
        if isImport:
            data = '\x00\x01\x00\x00'

        log().log('Sending SSI edit begin (CLI_SSI_EDIT_BEGIN)')
        #self.sendSNAC(0x13, 0x11, 0x11, data)
        self.sendSNAC(0x13, 0x11, 0, '')

    def sendSSIEditEnd(self):
        '''
        SNAC(13,12)     CLI_SSI_EDIT_END    

        This snac used after SSI modification to commit transaction started by SNAC(13,11). 
        See also snac list for SSI service here.
        '''
        log().log('Sending SSI edit end (CLI_SSI_EDIT_END)')
        self.sendSNAC(0x13, 0x12, 0, '')

    def sendMessage(self, message, thruServer = True, ack = False,
        autoResponse = False, offline = False):

        # Channel 1       Channel 1 message format (plain-text messages) 
        # Channel 2       Channel 2 message format (rtf messages, rendezvous)    
        # Channel 4       Channel 4 message format (typed old-style messages)

        user = message.getUser()
        uin = message.getUIN()
        log().log("Sending message to %s (%s)" % (user, uin))

        channel = 1
        channel = struct.pack('!H', channel)
        data = genCookie() + channel + struct.pack('!B', len(uin)) + uin

        # 05        byte        fragment identifier (array of required capabilities)    
        # 01        byte        fragment version    
        # xx xx     word        Length of rest data 
        # xx ...    array       byte array of required capabilities (1 - text)

        # 01        byte        fragment identifier (text message)  
        # 01        byte        fragment version    
        # xx xx     word        Length of rest data
        t = "\x05\x01\x00\x03\x01\x01\x02"

        # 00 00     word        Message charset number  
        # ff ff     word        Message language number 
        # xx ..     string (ascii)      Message text string

        log().log("Sending %d '%s'" % (len(message.getContents()), message.getContents()))

        charSet = 3
        charSubSet = 0

        t += '\x01\x01' + struct.pack('!3H', len(message.getContents()) + 4, charSet, charSubSet)

        print 'With length:\n', coldump(t)

        t += message.getContents()

        outMsg = data + tlv(2, t)

        if ack:
            outMsg = outMsg + tlv(3, '')
        if autoResponse:
            outMsg = outMsg + tlv(4, '')
        if offline:
            log().log('Sending message through server (user is offline)')
            outMsg = outMsg + tlv(6, '')

        self.sendSNAC(0x04, 0x06, 0, outMsg)

    def sendKeepAlive(self):
        ''' 0x05 - Keep alive
        '''
        self.sendFLAP(0x05, '')


def _test():

    p = Protocol()
    p.connect('login.icq.com', 5190)

    buf = p.read()
    log().packetin(buf)

    p.sendAuth("203153632")
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

    using_proxy = 0

    if using_proxy == 0:
        s = ISocket(host, int(port))
        s.connect()
    else:
        s = HttpProxy('localhost', 1080)
        #s = Socks5Proxy('localhost', 1080)
        s.connect(host, int(port))

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

def _test_new_uin():

    p = Protocol()
    #p.connect('login.icq.com', 5190)
    #p.connect('205.188.5.92', 5190)

    p.sendHelloServer()

    ch, b, c = p.readFLAP(buf)
    snac = p.readSNAC(c)

    print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
    print 'for this snac: ', snac

    tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
    func = getattr(p, tmp)

    func(snac[5])

if __name__ == '__main__':
    _test()
    #_test_new_uin()

    if 0:
        p = Protocol()

        buf = restoreFromFile('pic.req')
        print coldump(buf)

        ch, b, c = p.readFLAP(buf)
        snac = p.readSNAC(c)
        print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
        print 'for this snac: ', snac

        tlvs = readTLVs(snac[5])

        p.proc_2_23_13(snac[5])

# ---
