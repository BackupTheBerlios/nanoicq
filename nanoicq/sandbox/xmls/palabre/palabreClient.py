# -*- coding: utf-8 -*-

import socket
import asynchat
import xml.dom.minidom as xmldom
import xml.sax.saxutils as SAX
import string
import md5, random
import cPickle
from traceback import *

from mx import DateTime

from util import *
from palabre import config, logging, version, escape_string
from Message import mtypes

from err import ERRORS, ERRORS_lookup

if config.get("database", "type") == "mysql":
    import MySQLdb as DB
elif config.get("database", "type") == "firebird":
    import kinterbasdb as DB
else:
    raise InnerException(33, ERRORS[33])

def Q(v):
    """ Shortcut for saxutils.quoteattr """
    return SAX.quoteattr(v)

def NUL(v):
    if v is None:
        return 0
    return v

def STRNUL(v):
    if v is None:
        return ''
    return v

def NEGNUL(v):
    if v is None:
        return -1
    if type(v) != type(1):
        raise Exception("Value of type " + str(type(v)) + " passed to NEGNULL, must be integer")
    return v


class InnerException(Exception):
    def __init__(self, errno, msg):
        Exception.__init__(self, msg)
        self.msg = msg
        self.errno = errno

    def __str__(self):
        return "'%s' error='%d'" % (self.msg, self.errno)


class FakeException(Exception):
    ''' For debug only '''
    pass


_roomTemplate = '''
                <room id='%d' 
                        name=%s

                        creatorid='%d'
                        operatorid='%d'

                        languageid='%d'
                        temporary='%d'
                        passwordProtected='%d'

                        pvtPassword = '%s'
                        publicPassword = '%s'

                        moderationAllowed='%d'
                        roomManagementLevel='%d'
                        userManagementlevel='%d'

                        numberOfUsers='%d'
                        numberOfSpectators='%d'

                        lastUpdateUserId='%d'
                        allowedGroupId='%d'
                        pvtPasswordProtected='%d'
                />
'''

_roomQuery = '''
            select
                id,
                name,

                creatorid,
                operatorid,

                languageid,
                temporary,
                passwordProtected,

                pvtPassword,
                publicPassword,

                moderationAllowed,
                roomManagementLevel,
                userManagementlevel,

                numberOfUsers,
                numberOfSpectators,

                lastUpdateUserId,
                allowedGroupId,
                pvtPasswordProtected

            from rooms %s order by name 
'''

class PalabreClient(asynchat.async_chat):

    def __init__(self,server, conn, addr, db):
        self.ids = None

        # Asynchat initialisation ... (main class for sending and receiving messages */
        asynchat.async_chat.__init__ (self, conn)

        # Is client silent or not, it's session level attribute
        self.silent = 0
        self.silentPeriod = 0
        self.silentStart = None

        self.server = server
        self.conn = conn

        # Database connection
        self.db = db

        # Adresse Ip ?
        self.addr = addr[0]
        print '>>>', self.addr

        # Null character
        self.carTerm = "\0"

        # Inherited from asynchat ..
        self.set_terminator (self.carTerm)

        # String de r√©ception des donn√©es
        self.data = ""

        # Nickname vide tant qu'on a pas recu la balise nickname
        self.nickName = ""

        # Donc on est pas encore logu√©
        self.loggedIn = 0

        # Liste des rooms o√π le client est connect√©
        self.allMyRooms = {}

        # A t'il fournit le mot magique ?
        self.isRoot = 0

        logging.info("Connection initialized for %s" % self.addr)

    def listBlockedUsers(self):
        try:
            c = self.db.cursor()
            s = "select id, name from users where isblocked = 1"
            c.execute(s)

            out = ["<listblockedusers error='0' >"]
            rs = c.fetchall()

            if rs is not None:
                for r in rs:
                    out.append("<user id='%d' name='%s' />" % (r[0], escape_string(string.strip(r[1])) ))

            out.append("</listblockedusers>") 
            self.clientSendMessage("\n".join(out))
        except InnerException, exc:
            out = "<listblockedusers msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            out = "<listblockedusers error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def silentUser(self, uid, attrs):
        period = int(attrs["period"])
        try:
            if period is None or period <= 0:
                raise InnerException(29, ERRORS[29])

            c = self.db.cursor()
            s = 'select u.id from users u where id = %d' % uid
            c.execute(s)

            out = "<silentuser error='0' id='%d' />" % uid
            rs = c.fetchone()
            if rs is None:
                raise InnerException(32, ERRORS[32] % uid)

            self.server.silentUser(uid, period)
 
            self.clientSendMessage(out)
        except InnerException, exc:
            out = "<silentuser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            out = "<silentuser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def locateUser(self, uid):
        c = self.db.cursor()
        try:
            s = 'select r.id, r.name from rooms r where r.id in (select rooms_id from users_rooms where users_id = %d)' % uid
            c.execute(s)

            out = ["<locateuser error='0' id='%d' >" % uid]
            rs = c.fetchall()
            if rs is None:
                raise InnerException(32, ERRORS[32] % uid)

            for r in rs:
                out.append("<room id='%d' name='%s' />" % (r[0], escape_string(string.strip(r[1])) ))

            out.append("</locateuser>") 
            self.clientSendMessage("\n".join(out))
        except InnerException, exc:
            safeClose(c)
            out = "<locateuser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<locateuser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def listGroups(self, sesId = None):
        print 'listing groups...'

        try:
            c = self.db.cursor()
            c.execute("select id, name, mlevel from groups order by name")
            rs = c.fetchall()

            out = ["<groups error='0'>"]
            for r in rs:
                print r
                out.append("<group id='%d' name=%s moderationLevel='%d' />" %\
                    (r[0], Q(string.strip(r[1])), r[2]))
                print out
            out.append("</groups>")
            self.clientSendMessage("\n".join(out))
        except InnerException, exc:
            out = "<groups msg=%s />"
            safeClose(c)
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            out = "<groups error='-1' msg=%s />"
            safeClose(c)
            self.clientSendMessage( out % Q(str(exc)) )

    def createGroup(self, sesId = None, name = None, moderationLevel = None):
        print 'creating group...', name, moderationLevel

        out = "<creategroup error='%d' msg=%s />"
        try:
            c = self.db.cursor()
            s = "insert into groups (name, mlevel) values ('%s', %d)" %\
                (escape_string(name), int(moderationLevel))
            print s
            c.execute(s)
            self.db.commit()

            c.execute("select id, name, mlevel from groups where name = '%s' and mlevel='%d'" %\
                (escape_string(name), int(moderationLevel)))

            r = c.fetchone()

            out = ["<creategroup error='0'>"] 
            out.append("<group id='%d' name='%s' moderationLevel='%d' />" %\
                    (r[0], escape_string(string.strip(r[1])), r[2]))
            out.append("</creategroup>")
            self.clientSendMessage("\n".join(out))
            print "creategroup done"
        except InnerException, exc:
            out = "<creategroup msg=%s />"
            sexc = str(exc)
            if sexc.find("-802") >= 0:
                errorMessage = "Unable to create group, name is too long, must be less than 250 characters"
            elif sexc.find("-803") >= 0:
                errorMessage = "Unable to create group with duplicate name"
            else:
                errorMessage = sexc
            self.clientSendMessage( out % Q(errorMessage) )
        except Exception, exc:
            out = "<creategroup error='-1' msg=%s />"
            sexc = str(exc)
            if sexc.find("-802") >= 0:
                errorMessage = "Unable to create group, name is too long, must be less than 250 characters"
            elif sexc.find("-803") >= 0:
                errorMessage = "Unable to create group with duplicate name"
            else:
                errorMessage = sexc
            self.clientSendMessage( out % Q(errorMessage) )

    def getGroupProperties(self, sesId = None, gid = None):
        print 'retrieving group properties...', gid

        try:
            c = self.db.cursor()
            c.execute("select id, name, mlevel from groups where id=%d" % int(gid))

            r = c.fetchone()
            if r is None:
                raise InnerException(1, ERRORS[1] % int(gid))

            out = "<getgroupproperties error='0' id='%d' name='%s' moderationLevel='%d' />" %\
                (r[0], escape_string(string.strip(r[1])), r[2])
            self.clientSendMessage(out)
        except InnerException, exc:
            out = "<getgroupproperties id='%d' msg=%s />"
            self.clientSendMessage( out % ( int(gid), Q(str(exc)) ) )
        except Exception, exc:
            out = "<getgroupproperties error='-1' id='%d' msg=%s />"
            self.clientSendMessage( out % ( int(gid), Q(str(exc)) ) )

    # ® •È• 1 Ø‡Æ°´•¨†. •·´® ™Æ¨≠†‚† password protected, ‚Æ£§† „ ≠•• §Æ´¶•≠ °Î‚Ï property password ® •£Æ ≠†§Æ §Æ°†¢®‚Ï ¢

    def groupLookUp(self, sesId = None, name = None):
        print 'group look up...', name

        try:
            if name is None:
                raise InnerException(17, ERRORS[17] % 'name')

            c = self.db.cursor()
            s = "select id, name, mlevel from groups where name = '%s'" % escape_string(name)
            print s
            c.execute(s)

            r = c.fetchone()
            if r is None:
                raise InnerException(2, ERRORS[2] % escape_string(name))

            out = "<grouplookup error='0' id='%d' name='%s' moderationLevel='%d' />" %\
                (r[0], escape_string(string.strip(r[1])), r[2])
            self.clientSendMessage(out)
        except InnerException, exc:
            out = "<grouplookup name='%s' msg=%s />"
            self.clientSendMessage( out % ( escape_string(str(name)), Q(str(exc)) ) )
        except Exception, exc:
            out = "<grouplookup error='-1' name='%s' msg=%s />"
            self.clientSendMessage( out % ( escape_string(str(name)), Q(str(exc)) ) )

    def userLookUp(self, sesId = None, name = None):
        print 'user look up...', name

        try:
            if name is None:
                raise InnerException(17, ERRORS[17] % 'name')

            c = self.db.cursor()
            s = "select id, name from users where name = '%s'" % escape_string(name)
            print s
            c.execute(s)

            r = c.fetchone()
            if r is None:
                raise InnerException(7, ERRORS[7] % escape_string(name))

            out = ["<userlookup error='0' >"]
            out.append("<client id='%d' name = '%s' />" % (r[0], name))
            out.append("</userlookup>")

            self.clientSendMessage("\n".join(out))
        except InnerException, exc:
            out = "<userlookup name='%s' msg=%s />"
            self.clientSendMessage( out % ( escape_string(str(name)), Q(str(exc)) ) )
        except Exception, exc:
            out = "<userlookup error='-1' name='%s' msg=%s />"
            self.clientSendMessage( out % ( escape_string(str(name)), Q(str(exc)) ) )

    def deleteGroup(self, sesId = None, gid = None):
        print 'delete group...', gid

        gid = int(gid)

        try:
            c = self.db.cursor()
            c.execute("select id, name, mlevel from groups where id=%d" % gid)

            r = c.fetchone()
            if r is None:
                raise InnerException(1, ERRORS[1] % int(gid))

            moderationLevel = int(r[2])
            s = "select moderationLevel from users where id = %d" % self.ids

            try:
                print s
                c.execute(s)
                r = c.fetchone()
                if r is None or len(r) <= 0:
                    raise InnerException(3, ERRORS[3] % self.ids)
                print r
                mlevel = int(r[0])
                if mlevel < moderationLevel:
                    raise InnerException(38, ERRORS[38]\
                        % (self.ids, mlevel, moderationLevel))
            except:
                raise

            self.db.commit()
            self.db.begin()
            try:
                s = "delete from groups where id = %d" % gid
                print s
                c.execute(s)

                s = "update users set gid = null where gid = %d" % gid
                print s
                c.execute(s)

                self.db.commit()
            except:
                self.sb.rollback()
                raise

            out = "<deletegroup error='0' id='%d' />" % gid
            self.clientSendMessage(out)
        except InnerException, exc:
            out = "<deletegroup id='%d' msg=%s />"
            self.clientSendMessage( out % ( int(gid), Q(str(exc)) ) )
        except Exception, exc:
            out = "<deletegroup error='-1' id='%d' msg=%s />"
            self.clientSendMessage( out % ( int(gid), Q(str(exc)) ) )

    def setGroupProperties(self, sesId = None, gid = None, name = None, moderationLevel = None):
        print 'retrieving group properties...', gid

        try:
            c = self.db.cursor()

            c.execute("select id, name, mlevel from groups where id=%d" % int(gid))

            r = c.fetchone()
            if r is None:
                raise InnerException(1, ERRORS[1] % int(gid))

            sl = []
            s = 'update groups set '
            if name is not None:
                sl.append(" name = '%s' " % escape_string(name))
            if moderationLevel is not None:
                sl.append(" mlevel = %d " % int(moderationLevel))
            s += ", ".join(sl)
            s += ' where id = %d' % int(gid)

            print s
            self.db.commit()
            self.db.begin()
            c.execute(s)
            self.db.commit()            

            out = "<setgroupproperties error='0' id='%d' />" % int(gid)
            self.clientSendMessage(out)
        except InnerException, exc:
            out = "<setgroupproperties msg=%s />"
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            out = "<setgroupproperties error='-1' msg=%s />"
            self.clientSendMessage( out % Q(str(exc)) )

    def listMembers(self, sesId = None, gid = None):
        print 'retrieving group members...', gid

        try:
            c = self.db.cursor()
            s = 'select u.id, u.name from users u where gid = %d' % int(gid)
            c.execute(s)

            out = ["<listmembers error='0' id='%d' >" % int(gid)]

            rs = c.fetchall()
            for r in rs:
                out.append("<client id='%d' name=%s />" %\
                    (r[0], Q(string.strip(r[1]))) )

            out.append("</listmembers>");
 
            self.clientSendMessage("\n".join(out))
        except InnerException, exc:
            out = "<listmembers msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            out = "<listmembers error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def getUserProperties(self, sesId = None, uid = None):
        print 'retrieving user properties... %d' % int(uid)

        try:
            c = self.db.cursor()
            s = ''' select 
                        u.id, 
                        u.name, 
                        u.gid, 
                        u.languageid, 
                        u.isblocked, 
                        u.moderationlevel, 
                        u.roommanagementlevel, 
                        u.usermanagementlevel, 
                        u.lastIP,
                        u.groupUserManagementLevel,
                        u.dbOperator
                from users u where id = %d ''' % int(uid)
            c.execute(s)

            out = ["<getuserproperties error='0' id='%d' >" % int(uid)]

            rs = c.fetchall()
            if len(rs) == 0:
                raise InnerException(6, ERRORS[6] % int(uid))

            for r in rs:
                print r
                out.append("<client id='%d' name=%s groupid='%d' languageid='%d' isblocked='%d' moderationlevel='%d' roommanagementlevel='%d' usermanagementlevel='%d' lastip=%s groupUserManagementLevel='%d' dbOperator='%d' />" %\
                    (
                        r[0], Q(string.strip(r[1])), NEGNUL(r[2]), r[3], r[4], r[5], r[6], r[7], Q(string.strip(STRNUL(r[8]))), NUL(r[9]), NUL(r[10])
                    )
                )

            out.append("</getuserproperties>");
 
            self.clientSendMessage("\n".join(out))
        except InnerException, exc:
            out = "<getuserproperties id='%d' msg=%s />" 
            self.clientSendMessage( out % ( int(uid), Q(str(exc)) ) )
        except Exception, exc:
            out = "<getuserproperties error='-1' id='%d' msg=%s />" 
            self.clientSendMessage( out % ( int(uid), Q(str(exc)) ) )

    def setUserProperties(self, sesId = None, attrs = {}):
        uid = int(attrs['id'])
        del attrs['id']

        print 'setting user properties... %d' % int(uid)

        c = None
        try:
            c = self.db.cursor()

            c.execute("select id from users where id=%d" % int(uid))

            r = c.fetchone()
            if r is None:
                raise InnerException(6, ERRORS[6] % int(uid))


            sl = []
            s = 'update users set '

            if attrs.has_key('name'):
                sl.append(" name = %s " % escape_string(attrs['name']))
            if attrs.has_key('languageid'):
                sl.append(" languageid = %d " % int(attrs['languageid']))
            if attrs.has_key('roommanagementlevel'):
                sl.append(" roommanagementlevel = %d " % int(attrs['roommanagementlevel']))
            if attrs.has_key('usermanagementlevel'):
                sl.append(" usermanagementlevel = %d " % int(attrs['usermanagementlevel']))
            if attrs.has_key('moderationlevel'):
                sl.append(" moderationlevel = %d " % int(attrs['moderationlevel']))
            if attrs.has_key('password'):
                sl.append(" password = %s " % escape_string(attrs['password']))

            if attrs.has_key('dbOperator'):
                sl.append(" dbOperator = %d " % int(attrs['dbOperator']))
            if attrs.has_key('groupUserManagementLevel'):
                sl.append(" groupUserManagementLevel = %d " % int(attrs['groupUserManagementLevel']))
            if attrs.has_key('groupid'):
                gid = int(attrs['groupid'])
                sl.append(" gid = %d " % gid)

                # Check group existance
                c.execute("select id from groups where id=%d" % gid)
                r = c.fetchone()
                if r is None:
                    raise InnerException(1, ERRORS[1] % gid)

            isblocked = 0
            if attrs.has_key('isblocked'):
                isblocked = int(attrs['isblocked'])
                sl.append(" isblocked = %d " % isblocked)

            s += ",".join(sl)
   
            s += ' where id = %d' % int(uid)
            print s

            self.db.commit()
            self.db.begin()
            c.execute(s)
            self.db.commit()

            out = "<setuserproperties error='0' id='%d' />" % int(uid)
            self.clientSendMessage(out)
            safeClose(c) 

            if isblocked == 1:
                self.server.blockClient(int(uid))

        except InnerException, exc:
            safeClose(c)
            out = "<setuserproperties msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<setuserproperties error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def getRoomList(self, sesId = None):
        print 'retrieving room list...'

        c = None
        try:
            c = self.db.cursor()

            # Pass empty parameter
            s = _roomQuery % ""
            c.execute(s)

            out = ["<getroomlist error='0' >"]

            rs = c.fetchall()
            for r in rs:

                #fil = open('s.pickle', 'wb')
                #cPickle.dump(r, fil)
                #fil.close()

                out.append(_roomTemplate %\
                    (r[0], Q(string.strip(r[1])), NUL(r[2]), NUL(r[3]), NUL(r[4]), NUL(r[5]), NUL(r[6]),
                        string.strip(STRNUL(r[7])), 
                        string.strip(STRNUL(r[8])), 
                        NUL(r[9]), 
                        NUL(r[10]), 
                        NUL(r[11]),
                        NUL(r[12]), 
                        NUL(r[13]),
                        NUL(r[14]),
                        NUL(r[15]),
                        NUL(r[16])
                        )
                )

            print 'pass #4'
            out.append("</getroomlist>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<getroomlist msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<getroomlist error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def getRoomProperties(self, sesId = None, rid = None):
        print 'retrieving room properties...'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            c.execute("select id from rooms where id=%d" % int(rid))

            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % int(rid))

            # Pass where clause
            s = _roomQuery % ("where id = %d" % rid)
            print s

            c.execute(s)

            out = ["<getroomproperties error='0' >"]

            rs = c.fetchall()
            for r in rs:
                print 'R=', len(r)
                out.append(_roomTemplate %\
                    (r[0], Q(string.strip(r[1])), 
                        NUL(r[2]), 
                        NUL(r[3]), 
                        NUL(r[4]), 
                        NUL(r[5]), 
                        NUL(r[6]), 
                        string.strip(STRNUL(r[7])), 
                        string.strip(STRNUL(r[8])), 
                        NUL(r[9]), 
                        NUL(r[10]), 
                        NUL(r[11]),
                        NUL(r[12]), 
                        NUL(r[13]),
                        NUL(r[14]),
                        NUL(r[15]),
                        NUL(r[16])
                        )
                )

            s = "select users_id from allowed_users_rooms where rooms_id=%d order by users_id" % rid
            c.execute(s)
            rs = c.fetchall()
            for r in rs:
                out.append("<client id='%d' />" % r[0])

            out.append("</getroomproperties>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<getroomproperties msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<getroomproperties error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def setRoomSecurity(self, attrs):

        # Set password, room had no password
        # <setroomsecurity id='1'
        #    pvtPasswordProtected='1' 
        #    newPvtPassword='password' />

        # Set password, room had password
        # <setroomsecurity id='1'
        #    pvtPasswordProtected='1' 
        #    pvtPassword='oldpassword'
        #    newPvtPassword='newpassword' />

        # Remove password, room had password
        # <setroomsecurity id='1'
        #    pvtPasswordProtected='0' 
        #    pvtPassword='oldpassword' />

        try:
            c = self.db.cursor()

            rid = self._getIntAttr("id", attrs)
            pvtPasswordProtected = self._getIntAttr("pvtPasswordProtected", attrs)


            if pvtPasswordProtected not in [0, 1]:
                raise InnerException(50, ERRORS[50])

            newPvtPassword = None
            if attrs.has_key('newPvtPassword'):
                newPvtPassword = attrs['newPvtPassword']
                if len(newPvtPassword) == 0:
                    raise InnerException(49, ERRORS[49])

            c.execute("select id, pvtPasswordProtected, pvtPassword from rooms where id=%d" % rid)
            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % rid)

            dbPvtPasswordProtected = NUL(r[1])
            dbPvtPassword = STRNUL(string.strip(r[2]))

            if dbPvtPasswordProtected == 1:
                pvtPassword = self._getStrAttr("pvtPassword", attrs)

                if pvtPassword != dbPvtPassword:
                    #raise Exception("Invalid pvtPassword %s/%s" % (pvtPassword, dbPvtPassword))
                    raise InnerException(14, ERRORS[14])

                if pvtPasswordProtected == 1:
                    # Set password, room had password
                    # <setroomsecurity id='1'
                    #    pvtPasswordProtected='1' 
                    #    pvtPassword='oldpassword'
                    #    newPvtPassword='newpassword' />
                    if newPvtPassword is None:
                        raise InnerException(48, ERRORS[48])
                    s = "update rooms set pvtPasswordProtected = 1, pvtPassword = '%s' where id = %d" % ( escape_string(newPvtPassword), rid )
                else:
                    # Remove password, room had password
                    # <setroomsecurity id='1'
                    #    pvtPasswordProtected='0' 
                    #    pvtPassword='oldpassword' />
                    s = "update rooms set pvtPasswordProtected = 0, pvtPassword = '' where id = %d" % ( rid )
            else:
                if pvtPasswordProtected == 1:
                    # Set password, room had no password
                    # <setroomsecurity id='1'
                    #    pvtPasswordProtected='1' 
                    #    newPvtPassword='password' />
                    if newPvtPassword is None:
                        raise InnerException(48, ERRORS[48])
                    s = "update rooms set pvtPasswordProtected = 1, pvtPassword = '%s' where id = %d" % ( escape_string(newPvtPassword), rid )
                else:
                    # Remove password
                    s = "update rooms set pvtPasswordProtected = 0, pvtPassword = '' where id = %d" % ( rid )

            print s

            self.db.commit()
            self.db.begin()
            c.execute(s)
            self.db.commit()

            out = "<setroomsecurity id='%d' error='0' />" 
            self.clientSendMessage(out % rid)

        except InnerException, exc:
            safeClose(c)
            out = "<setroomsecurity msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<setroomsecurity error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def setRoomProperties(self, sesId = None, rid = None, attrs = {}):
        print 'setting room properties...'

        rid = int(rid)
        c = None

        try:
            print attrs
            c = self.db.cursor()

            c.execute("select id, pvtPasswordProtected, pvtPassword from rooms where id=%d" % int(rid))

            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % int(rid))

            pvtPasswordProtected = NUL(r[1])
            pvtPassword = string.strip(STRNUL(r[2]))

            if pvtPasswordProtected == 1:
                if attrs.has_key('pvtPassword'):
                    rawPvtPassword = attrs['pvtPassword']
                    if rawPvtPassword != pvtPassword:
                        #raise Exception("Room is password protected, invalid pvtPassword %s/%s" % (rawPvtPassword, pvtPassword))
                        raise InnerException(25, ERRORS[25])
                else:
                    raise InnerException(27, ERRORS[27])
                    #sl.append(" pvtPassword = '%s' " % escape_string(attrs['pvtPassword']))

            sl = []
            s = 'update rooms set '

            if attrs.has_key('name'):
                sl.append(" name = '%s' " % escape_string(attrs['name']))
            if attrs.has_key('languageid'):
                sl.append(" languageid = %d " % int(attrs['languageid']))
            #if attrs.has_key('creatorid'):
            #    sl.append(" creatorid = %d " % int(attrs['creatorid']))
            if attrs.has_key('operatorid'):
                sl.append(" operatorid = %d " % int(attrs['operatorid']))

            # Special handling, if we've received publicPassword, then
            # passwordProtected must be specified
            if attrs.has_key('publicPassword'):

                if attrs.has_key('passwordProtected'):
                    protect = int(attrs['passwordProtected'])
                    if protect == 1:
                        sl.append(" publicpassword = '%s' " % escape_string(attrs['publicPassword']))

            if attrs.has_key('temporary'):
                sl.append(" temporary = %d " % int(attrs['temporary']))
            if attrs.has_key('allowedUsers'):
                sl.append(" allowedUsers = %d " % int(attrs['allowedUsers']))

            # Special handling, if we've received publicPassword, then
            # passwordProtected must be specified
            if attrs.has_key('passwordProtected'):
                protect = int(attrs['passwordProtected'])
                if protect == 1:
                    if attrs.has_key('publicPassword'):
                        pp = attrs['publicPassword']
                        if len(pp) == 0:
                            raise InnerException(24, ERRORS[24])
                    else:
                        raise InnerException(23, ERRORS[23])
                sl.append(" passwordProtected = %d " % protect)

            if attrs.has_key('moderationAllowed'):
                sl.append(" moderationAllowed = %d " % int(attrs['moderationAllowed']))
            if attrs.has_key('roomManagementLevel'):
                sl.append(" roomManagementLevel = %d " % int(attrs['roomManagementLevel']))
            if attrs.has_key('userManagementlevel'):
                sl.append(" userManagementlevel = %d " % int(attrs['userManagementlevel']))

            if attrs.has_key('allowedGroupId'):
                # We need to check group existence
                allowedGroupId = int(attrs['allowedGroupId'])
                checkGroupSql = "select id from groups where id = %d" % allowedGroupId
                checkGroupCursor = self.db.cursor()
                checkGroupCursor.execute(checkGroupSql)
                rs = checkGroupCursor.fetchone()
                print 'ALLOWEDGROUP', rs
                if rs is None or len(rs) == 0:
                    raise InnerException(31, ERRORS[31] % allowedGroupId)

                sl.append(" allowedGroupId = %d " % allowedGroupId)

            sl.append(" lastUpdateUserId = %d " % self.ids)

            s += ", ".join(sl)      
            s += ' where id = %d' % int(rid)
            print s
 
            self.db.commit()
            self.db.begin()
            c.execute(s)
            self.db.commit()

            out = ["<setroomproperties error='0' >"]
            out.append("</setroomproperties>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<setroomproperties msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<setroomproperties error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def removeAllowedUser(self, sesId = None, rid = None, uid = None):
        print 'removing allowed user'

        rid = int(rid)
        uid = int(uid)
        c = None

        try:
            c = self.db.cursor()
            s = ''

            raise InnerException(19, ERRORS[19])
            print s
 
            c.execute(s)

            out = ["<removealloweduser error='0' >"]
            out.append("</removealloweduser>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<removealloweduser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<removealloweduser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
 
    def appendNewAllowedUser(self, sesId = None, rid = None, uid = None):
        print 'adding new allowed user'

        rid = int(rid)
        uid = int(uid)
        c = None

        try:
            c = self.db.cursor()
            s = ''

            raise InnerException(19, ERRORS[19])
            print s
 
            c.execute(s)

            out = ["<addnewalloweduser error='0' >"]
            out.append("</addnewalloweduser>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<addnewalloweduser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<addnewalloweduser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def deleteAllowedUser(self, attrs):
        c = self.db.cursor()

        try:

            uid = self._getIntAttr("uid", attrs)
            rid = self._getIntAttr("rid", attrs)

            self.db.commit()
            self.db.begin()

            s = "select users_id from allowed_users_rooms where rooms_id=%d order by users_id" % rid
            print s
            c.execute(s)
            rs = c.fetchall()

            found = False
            for r in rs:
                if r[0] == uid:
                    found = True
                    break

            if not found:
                raise InnerException(42, ERRORS[42] % (uid, rid))

            s = "delete from allowed_users_rooms where (users_id=%d and rooms_id=%d)" % (uid, rid)
            print s
            c.execute(s)
            self.db.commit()

            self.clientSendMessage("<deletealloweduser uid='%d' rid='%d' error='0' />" % (uid, rid))
            safeClose(c) 

        except InnerException, exc:
            safeClose(c)
            out = "<deletealloweduser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<deletealloweduser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )


    def listAllowedUser(self, attrs):
        c = self.db.cursor()

        try:
            rid = self._getIntAttr("rid", attrs)

            self.db.commit()
            self.db.begin()

            out = ["<listalloweduser error='0' rid='%d' >" % rid]

            s = "select id from rooms where id = %d" % rid
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(4, ERRORS[4] % rid)

            s = "select users_id from allowed_users_rooms where rooms_id=%d order by users_id" % rid
            c.execute(s)
            rs = c.fetchall()
            for r in rs:
                s = "select name from users where id = %d" % r[0]
                c2 = self.db.cursor()
                c2.execute(s)
                rs2 = c2.fetchone()
                if rs2 is None or len(rs2) == 0:
                    raise InnerException(10, ERRORS[10] % r[0])
                out.append("<client id='%d' name=%s />" % (r[0], Q(string.strip(rs2[0]))))

            out.append("</listalloweduser>")
            self.clientSendMessage("\n".join(out))
            safeClose(c) 

        except InnerException, exc:
            safeClose(c)
            out = "<listalloweduser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<listalloweduser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def redirectUser(self, attrs):
        c = self.db.cursor()

        try:

            uid = self._getIntAttr("uid", attrs)
            to_rid = self._getIntAttr("ro_rid", attrs)
            from_rid = self._getIntAttr("from_rid", attrs)

            self.db.commit()
            self.db.begin()

            s = "select id from users where id = %d" % uid
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(6, ERRORS[6] % uid)

            s = "select id from rooms where id = %d" % to_rid
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(4, ERRORS[4] % to_rid)

            s = "select id from rooms where id = %d" % from_rid
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(4, ERRORS[4] % from_rid)

            s = "select users_id from allowed_users_rooms where rooms_id=%d order by users_id" % to_rid
            print s
            c.execute(s)
            rs = c.fetchall()

            found = False
            for r in rs:
                if r[0] == uid:
                    found = True
                    break
            if not found:
                raise InnerException(39, ERRORS[39] % (uid, to_rid))

            s = "select users_id from users_rooms where users_id=%d and rooms_id=%d order by users_id" % (uid, from_rid)
            print s
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(5, ERRORS[5] % (uid, from_rid))

            s = "update users_rooms set rooms_id=%d where users_id=%d and rooms_id=%d" % (to_rid, uid, from_rid)
            print s
            c.execute(s)

            self.db.commit()

            self.clientSendMessage("<redirectuser uid='%d' from_rid='%d' to_rid='%d' error='0' />" % (uid, from_rid, to_rid))
            safeClose(c) 

        except InnerException, exc:
            safeClose(c)
            out = "<redirectuser from_rid='%d' to_rid='%d' msg=%s />" 
            self.clientSendMessage( out % (from_rid, to_rid, Q(str(exc))) )
        except Exception, exc:
            safeClose(c)
            out = "<redirectuser error='-1' from_rid='%d' to_rid='%d' msg=%s />" 
            self.clientSendMessage( out % (from_rid, to_rid, Q(str(exc))) )


    def addAllowedUser(self, attrs):
        #allowedUsers ´„ÁË• Ø•‡•§†¢†‚Ï Æ‚§•´Ï≠Î¨ Á†≠™Æ¨ ™†™ listMembers
        #C: <listAllowedUser roomId="2">
        #C: <deleleAllowedUser rommId="2" userId="4">
        #C: <addAllowedUser rommId="2" userId="4">

        c = self.db.cursor()

        try:

            uid = self._getIntAttr("uid", attrs)
            rid = self._getIntAttr("rid", attrs)

            self.db.commit()
            self.db.begin()

            s = "select users_id from allowed_users_rooms where rooms_id=%d order by users_id" % rid
            c.execute(s)
            rs = c.fetchall()
            for r in rs:
                if r[0] == uid:
                    raise InnerException(35, ERRORS[35] % (uid, rid))

            s = "select id from users where id = %d" % uid
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(6, ERRORS[6] % uid)

            s = "select id from rooms where id = %d" % rid
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(4, ERRORS[4] % rid)

            s = "insert into allowed_users_rooms (users_id, rooms_id) values (%d, %d)" % (uid, rid)
            c.execute(s)
            self.db.commit()

            self.clientSendMessage("<addalloweduser uid='%d' rid='%d' error='0' />" % (uid, rid))
            safeClose(c) 

        except InnerException, exc:
            safeClose(c)
            out = "<addalloweduser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<addalloweduser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def createRoom(self, attrs, child):
        print 'creating new room'

        c = None

        try:

            if not attrs.has_key('name'):
                raise InnerException(26, ERRORS[26])

            c = self.db.cursor()
            #s = "select id from rooms where rooms.name like '%s'" % escape_string(attrs['name'])
            #s = "select id, name from rooms where name like 's%%'" % escape_string(attrs['name'])
            s = "select id, name from rooms order by name, id"

            print s
 
            c.execute(s)
            rs = c.fetchall()

            for r in rs:
                print r[0], r[1]
                i_id = int(r[0])
                i_name = string.strip(r[1])
                print i_id, i_name
                if i_name == escape_string(attrs['name']):
                    raise InnerException(28, ERRORS[28] % attrs['name'])

            keys = []
            s = []

            if attrs.has_key('name'):
                s.append( " '%s' " % escape_string(attrs['name']))
                keys.append("name")

            if attrs.has_key('languageid'):
                s.append(" %d " % int(attrs['languageid']))
                keys.append("languageid")
            if attrs.has_key('pvtPassword'):
                s.append( " '%s' " % escape_string(attrs['pvtPassword']))
                keys.append("pvtPassword")

            if attrs.has_key('publicPassword'):
                s.append( " '%s' " % escape_string(attrs['publicPassword']))
                keys.append("publicPassword")
 
            if attrs.has_key('temporary'):
                s.append(" %d " % int(attrs['temporary']))
                keys.append("temporary")

            if attrs.has_key('allowedUsers'):
                s.append(" %d " % int(attrs['allowedUsers']))
                keys.append("allowedUsers")

            if attrs.has_key('passwordProtected'):
                s.append(" %d " % int(attrs['passwordProtected']))
                keys.append("passwordProtected")

            if attrs.has_key('moderationAllowed'):
                s.append(" %d " % int(attrs['moderationAllowed']))
                keys.append("moderationAllowed")

            if attrs.has_key('roomManagementLevel'):
                s.append(" %d " % int(attrs['roomManagementLevel']))
                keys.append("roomManagementLevel")

            if attrs.has_key('userManagementlevel'):
                s.append(" %d " % int(attrs['userManagementlevel']))
                keys.append("userManagementlevel")

            # creatroid must be seperate
            s.append(" %d " % self.ids)
            keys.append("creatorid")

            # lastUpdateUserId must be seperate
            s.append(" %d " % self.ids)
            keys.append("lastUpdateUserId")

            s = "insert into rooms (%s) values (%s)" %\
                (",".join(keys), ",".join(s))

            self.db.commit()

            print s
            self.db.begin()
            c.execute(s)
            self.db.commit()

            room_name = escape_string(attrs['name'])
            c.execute("select id from rooms where name='%s'" % room_name)

            r = c.fetchone()
            if r is None:
                raise InnerException(46, ERRORS[46] % room_name)
            rid = r[0]

            clients = []
            for n in child:
                print n, n.nodeName
                if n.nodeName == 'client':
                    for p in n.attributes.items():
                        if p[0] == "id":
                            clients.append(int(p[1]))
            print clients

            if len(clients) > 0:
                s = "delete from allowed_users_rooms where "
                allowed = []
                for client in clients:
                    allowed.append("(users_id=%d and rooms_id=%d)" % (client, rid))
                s += " and ".join(allowed)
                c.execute(s)
                self.db.commit()

                s = "insert into allowed_users_rooms (users_id, rooms_id) values (%d, %d)"
                for client in clients:
                    c.execute(s % (client, rid))

                self.db.commit()
                print 'executed'

            out = ["<createroom error='0' id='%d' name=%s >" % ( rid, Q(attrs['name']) )]
            out.append("</createroom>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 

        except InnerException, exc:
            safeClose(c)
            out = "<createroom msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<createroom error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def delRoom(self, sesId = None, rid = None):
        print 'delete room'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            c.execute("select id from rooms where id=%d" % int(rid))

            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % int(rid))

            # FIMXE
            c.execute("select users.id, users.name from users where users.id in (select users_id from users_rooms where rooms_id = %d)" % int(rid))
            rs = c.fetchall()
            users = []
            if rs is not None and len(rs) > 0:
                for r in rs:
                    print r
                    users.append("#%d (%s)" % (int(r[0]), string.strip(r[1])))
                raise InnerException(30, ERRORS[30] % (int(rid), ", ".join(users)))

            s = 'delete from rooms where id = %d' % rid

            print s
 
            c.execute(s)
            self.db.commit()

            out = ["<delroom error='0' id='%d' >" % rid]
            out.append("</delroom>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 

        except InnerException, exc:
            safeClose(c)
            out = "<delroom msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<delroom error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def _getIntAttr(self, name, attrs):
        try:
            rc = int(self._getStrAttr(name, attrs))
        except ValueError, exc:
            raise InnerException(12, ERRORS[12] % name)
        return rc

    def _getStrAttr(self, name, attrs):
        if not attrs.has_key(name):
            raise InnerException(17, ERRORS[17] % name)
        try:
            rc = attrs[name]
        except:
            raise InnerException(12, ERRORS[12] % name)
        return rc

    def inviteUser(self, attrs):
        """
        C:
            Invite user id=33 to room 11
            <inviteuser uid='33' rid='11' />
        S:
            <inviteuser error='0' uid='33' rid='11' />
            or 
            <inviteuser error='2' msg='bad' />
        """
        try:
            c = self.db.cursor()

            uid = self._getIntAttr("uid", attrs)
            rid = self._getIntAttr("rid", attrs)

            self.server.inviteUser(uid, rid)

            out = "<inviteuser error='0' uid='%d' rid='%d' />" % (self.ids, rid)

            self.clientSendMessage(out)
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<inviteuser msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<inviteuser error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def joinAsSpectator(self, attrs):
        """
            C:
            <joinasspectator rid='1' /> 
                or
            <joinasspectator rid='1' publicPassword='password' />

            S:
            "<joinasspectator error='0' uid='12' rid='1' />"
                or
            "<joinasspectator error='2' msg='something wrong' />"
        """
        try:
            c = self.db.cursor()

            rid = self._getIntAttr("rid", attrs)
            if attrs.has_key("publicPassword"):
                publicPassword = attrs["publicPassword"]
            else:
                publicPassword = None

            s = "select name, passwordProtected, publicPassword from rooms where id = %d" % rid
            print s
            c.execute(s)
            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % rid)

            if int(r[1]) == 1:
                # Check password, room is password protected
                if publicPassword is None:
                    raise InnerException(8, ERRORS[8])
                if publicPassword != string.strip(r[2]):
                    raise InnerException(13, ERRORS[13])

            s = "select rooms_id from users_rooms where users_id = %d" % self.ids
            print s
            c.execute(s)

            rs = c.fetchall()
            for r in rs:
                #print 'Client #%d now in room #%d' % (self.ids, int(r[0]))
                if int(r[0]) == rid:
                    raise InnerException(36, ERRORS[36] % (self.ids, rid))


            out = "<joinasspectator error='0' uid='%d' rid='%d' />" % (self.ids, rid)

            self.db.commit()
            self.db.begin()
            s = "insert into users_rooms (users_id, rooms_id, spectator) values (%d, %d, %d)" % (self.ids, rid, 1)
            c.execute(s)
            self.db.commit()
 
            self.clientSendMessage(out)
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<joinasspectator msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<joinasspectator error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def joinRoom(self, sesId = None, rid = None, publicPassword = None):
        print 'joining room'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            print 'Client #%d attepting to join room #%d' % (self.ids, rid)

            #s = "update users_rooms"
            s = "select name, passwordProtected, publicPassword from rooms where id = %d" % rid
            print s
            c.execute(s)
            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % int(rid))

            print r
            if int(r[1]) == 1:
                # Check password, room is password protected
                if publicPassword is None:
                    raise InnerException(8, ERRORS[8])
                if publicPassword != string.strip(r[2]):
                    raise InnerException(13, ERRORS[13])

            s = "select rooms_id from users_rooms where users_id = %d" % self.ids
            print s
            c.execute(s)

            rs = c.fetchall()
            for r in rs:
                #print 'Client #%d now in room #%d' % (self.ids, int(r[0]))
                if int(r[0]) == rid:
                    raise InnerException(36, ERRORS[36] % (self.ids, rid))

            self.db.commit()
            self.db.begin()
            self.db.execute_immediate("insert into users_rooms (users_id, rooms_id) values (%d, %d)" % (self.ids, rid))
            self.db.commit()

            # Notify all clients in room
            self.server.handleClientInRoom(uid = self.ids, rid = rid, flag = EV_JOIN, name = self.name)
 
            out = "<joinroom error='0' uid='%d' rid='%d' />" % (self.ids, rid)
 
            self.clientSendMessage(out)
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<joinroom msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
        except Exception, exc:
            safeClose(c)
            out = "<joinroom error='-1' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

                     
    def leaveRoom(self, sesId = None, rid = None, attrs = None):
        print 'leaving room'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            print 'Client #%d attepting to leave room #%d' % (self.ids, rid)

            #s = "update users_rooms"
            s = "select name from rooms where id = %d" % rid
            print s
            c.execute(s)
            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % int(rid))

            s = "select rooms_id from users_rooms where users_id = %d" % self.ids
            print s
            c.execute(s)

            client_in_room = False
            rs = c.fetchall()
            for r in rs:
                print 'Client #%d now in room #%d' % (self.ids, int(r[0]))
                if int(r[0]) == rid:
                    client_in_room = True
                    break

            if not client_in_room:
                raise InnerException(43, ERRORS[43] % (self.ids, int(rid)))

            self.db.commit()
            self.db.begin()
            self.db.execute_immediate("delete from users_rooms where users_id = %d and rooms_id = %d" % (self.ids, rid))
            self.db.commit()

            # Notify all clients in room
            self.server.handleClientInRoom(uid = self.ids, rid = rid, flag = EV_LEAVE, name = self.name)
 
            out = "<leaveroom error='0' uid='%d' rid='%d' />" % (self.ids, rid)
 
            self.clientSendMessage(out)
            safeClose(c) 
        except InnerException, exc:
            safeClose(c)
            out = "<leaveroom rid='%d' msg=%s />" 
            self.clientSendMessage( out % (rid, Q(str(exc))) )
        except Exception, exc:
            safeClose(c)
            out = "<leaveroom error='-1' rid='%d' msg=%s />" 
            self.clientSendMessage( out % (rid, Q(str(exc))) )

    def createUser(self, attrs):
        try:
            c = self.db.cursor()
            name = self._getStrAttr("name", attrs)
            password = self._getStrAttr("password", attrs)
            if len(password) == 0:
                raise InnerException(20, ERRORS[20])

            s = "select id from users where name = '%s'" % escape_string(name)
            c.execute(s)
            rs = c.fetchone()
            if rs is not None:
                raise InnerException(34, ERRORS[34] % (name, rs[0]))

            self.db.commit()
            self.db.begin()
            s = "insert into users (name, upassword) values ('%s', '%s')" % (escape_string(name), escape_string(password))
            c.execute(s)
            self.db.commit()

            s = "select id from users where name = '%s'" % escape_string(name)
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(9, ERRORS[9] % (name))

            out = "<createuser error='0' name='%s' id='%d' />" % ((escape_string(name), rs[0]))
            self.clientSendMessage(out)

        except InnerException, exc:
            safeClose(c)
            out = "<createuser msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
        except Exception, exc:
            safeClose(c)
            out = "<createuser error='-1' msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
    
    def deleteUser(self, attrs):
        try:
            c = self.db.cursor()

            uid = self._getIntAttr("id", attrs)

            s = "select id, name from users where id = %d" % uid
            c.execute(s)
            rs = c.fetchone()
            if rs is None:
                raise InnerException(44, ERRORS[44] % uid)

            userName = string.strip(STRNUL(rs[1]))

            self.db.commit()
            self.db.begin()

            s = "delete from users_groups where users_id = %d" % uid
            c.execute(s)

            s = "delete from users_rooms where users_id = %d" % uid
            c.execute(s)

            s = "delete from allowed_users_rooms where users_id = %d" % uid
            c.execute(s)

            s = "delete from users where id = %d" % uid
            c.execute(s)

            self.db.commit()

            msg = """<error msg='User "%s" has been deleted. Disconnect requested.' />"""
            # Actually it's not block, just disconnect him
            self.server.blockClient(id, msg % userName)

            out = "<deleteuser error='0' id='%d' />" % (uid)
            self.clientSendMessage(out)

        except InnerException, exc:
            safeClose(c)
            out = "<deleteuser msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
        except Exception, exc:
            safeClose(c)
            out = "<deleteuser error='-1' msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
    
    def listUsers(self, sesId = None, rid = None, attrs = None):
        print 'list room users...'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            s = "select name from rooms where id = %d" % rid
            print s
            c.execute(s)
            r = c.fetchone()
            if r is None:
                raise InnerException(4, ERRORS[4] % int(rid))

            s = "select id, name, moderationLevel, roomManagementLevel from users where id in (select users_id from users_rooms where rooms_id = %d)" % rid
            print s

            c.execute(s)

            out = ["<listusers error='0' id='%d' >" % rid]

            rs = c.fetchall()
            c2 = self.db.cursor()

            for r in rs:
                s2 = "select spectator from users_rooms where users_id=%d and rooms_id = %d" % (r[0], rid)
                c2.execute(s2)
                rs2 = c2.fetchone()

                out.append("<client id='%d' name='%s' moderationLevel='%d' roomManagementLevel='%d' isspectator='%d' />" %\
                    (
                        r[0], 
                        escape_string(string.strip(r[1])),
                        NEGNUL(r[2]),
                        NEGNUL(r[3]),
                        NUL(rs2[0])
                    )
                )

            out.append("</listusers>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 

        except InnerException, exc:
            safeClose(c)
            out = "<listusers rid='%d' msg=%s />" 
            self.clientSendMessage( out % (rid, Q(str(exc))) )
        except Exception, exc:
            safeClose(c)
            out = "<listusers error='-1' rid='%d' msg=%s />" 
            self.clientSendMessage( out % (rid, Q(str(exc))) )

                     
    def handle_expt():
        """
            Tried to add this because there is sometimes a strange error in the logs
        """
        logging.debug("****PalabreClient.handle_expt: %s" % repr(self))

    def collect_incoming_data (self, data):
        """
            Everytime we collect data we add the data to the string self.data
            (Untill we encounter a terminator (\0)
        """
        self.data = self.data + data #.decode("utf-8")


    def found_terminator (self):
        """
            Terminator Character has been found !
            So the Xml string should be ok, we start parsing datas

        """

        # The complete XML string
        line = self.data

        # Reseting data for more data to come ...
        self.data = ''

        # Trying to parse
        self.doParse = 1

        # On essai
        # If string is not really XML this crash :
        line = "<?xml version='1.0' encoding='utf-8' ?>"+line
        #print line
        #line = unicode(line,'utf-8') #.encode('utf-8')
        #print line

        try:
            # Trying to parse data
            self.doc = xmldom.parseString(line)
        except:
            # Sending error message to inform user
            self.clientSendErrorMessage(msg="This is not a valid XML string")

            #Stop parsing
            self.doParse = 0

        if self.doParse:
            # really parsing Data
            self.parseData (data = self.doc)
            self.doc.unlink()

    def getInfo(self, attrs):
        c = self.db.cursor()
        try:
            clientUids = self.server.getConnectedUsers()

            out = [ "<info error='0' >" ]
            out.append("\t<connected>")
            for cuid in clientUids:
                out.append("\t\t<user id='%d' >" % cuid)
                c.execute("select rooms_id from users_rooms where users_id = %d" % cuid)
                rs = c.fetchall()
                for r in rs:
                    out.append("\t\t\t<room id='%d' />" % r[0])
                out.append("\t\t</user>")
            out.append("\t</connected>")

            out.append("\t<history range='last 10' >")
            s = "select first 10 userid, last_connected, lastip from connect_history order by last_connected desc"
            c.execute(s)
            rs = c.fetchall()

            delta = DateTime.DateTimeDelta(0, 10, 0, 0)

            for r in rs:
                dt = str(r[1])
                dz = DateTime.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S.00'))
                dz = dz + delta
                out.append("\t<entry uid='%d' connected='%s' ip='%s' />" % (r[0], dz, string.strip(r[2])) )
            out.append("\t</history>")

            out.append("</info>")
            self.clientSendMessage("\n".join(out))

            safeClose(c)
        except InnerException, exc:
            safeClose(c)
            out = "<info msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
        except Exception, exc:
            safeClose(c)
            out = "<info error='-1' msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
            

    def parseData(self,data):
        """
            OK terminator was found, and @data is parsed XML !
            We look for the node name and dispatch information to other methods
        """

        # Data must have child nodes
        if len(data.childNodes):
            # On attaque le XML #
            ## On definie des variables ##

            # The only node
            n = data.childNodes[0]
            #print 'NODE:', n, dir(n), n.childNodes

            # And the name of the node !
            # The name defines the function
            #
            node = str(n.nodeName)

            # All atributes of the node
            attrs = {}

            ## on recupere tous les attributs dans un dico ##
            # Looping the attributes
            for p in n.attributes.items():
                attrs[p[0]] = p[1].encode("utf-8")

            # if there is data inside (like CDATA ...)
            texte = ""

            # Getting inside text
            if len(n.childNodes):
                texte = n.childNodes[0].nodeValue
                texte = texte.encode("utf-8")

            # Ok let's start trying to guess what the request is
            if node == "help":
                self.clientSendHelp()
            elif node == "quit":
                self.clientQuit()

            # Client must be identified

            elif self.loggedIn:

                #print 'ATTRS:', attrs, dir(attrs)

                # He is sending a message
                if node == "message" or node == "m":
                    self.clientHandleMessage(attrs)

                # info
                elif node == "info":
                    self.getInfo(attrs)

                # users
                elif node == "createuser":
                    self.createUser(attrs)

                elif node == "deleteuser":
                    self.deleteUser(attrs)

                # security
                elif node == "setroomsecurity":
                    self.setRoomSecurity(attrs)

                # list groups
                elif node == "listgroups":
                    self.listGroups()

                # invitation
                elif node == "inviteuser":
                    self.inviteUser(attrs)

                # list groups
                elif node == "listblockedusers":
                    self.listBlockedUsers()

                # silent user
                elif node == "silentuser":
                    self.silentUser(int(attrs["id"]), attrs)

                # locate user
                elif node == "locateuser":
                    self.locateUser(int(attrs["id"]))

                # create group
                elif node == "creategroup":
                    self.createGroup(name = attrs["name"], moderationLevel = attrs["moderationLevel"])

                # get group properties
                elif node == "getgroupproperties":
                    self.getGroupProperties(gid = attrs["id"])

                # get group properties
                elif node == "grouplookup":
                    self.groupLookUp(name = attrs["name"])

                # delete group
                elif node == "deletegroup":
                    self.deleteGroup(gid = attrs["id"])

                # set group properties
                elif node == "setgroupproperties":
                    if attrs.has_key("name"):
                        g_name = attrs["name"]
                    else:
                        g_name = None

                    if attrs.has_key("moderationLevel"):
                        g_moderationLevel = attrs["moderationLevel"]
                    else:
                        g_moderationLevel = None

                    self.setGroupProperties(
                        gid = attrs["id"], name = g_name, 
                        moderationLevel = g_moderationLevel)
   
                # redirect
                elif node == "redirectuser":
                    self.redirectUser(attrs)

                # add allowed user
                elif node == "addalloweduser":
                    self.addAllowedUser(attrs)

                # list allowed user
                elif node == "listalloweduser":
                    self.listAllowedUser(attrs)

                # delete allowed user
                elif node == "deletealloweduser":
                    self.deleteAllowedUser(attrs)

                # get group members
                elif node == "listmembers":
                    self.listMembers(gid = attrs["id"])

                # get user properties
                elif node == "getuserproperties":
                    self.getUserProperties(uid = attrs["id"])

                # set user properties
                elif node == "setuserproperties":
                    self.setUserProperties(attrs = attrs)

                # get room list
                elif node == "getroomlist":
                    self.getRoomList()

                # 
                elif node == "userlookup":
                    self.userLookUp(name = attrs["name"])

                # get room properties
                elif node == "getroomproperties":
                    self.getRoomProperties(rid = attrs['id'])

                # set room properties
                elif node == "setroomproperties":
                    rid = attrs['id']
                    del attrs['id']
                    self.setRoomProperties(rid = rid, attrs = attrs)

                # create room
                elif node == "createroom":
                    self.createRoom(attrs = attrs, child = n.childNodes)

                # delete room
                elif node == "delroom":
                    self.delRoom(rid = attrs['id'])

                # join as spectator room
                elif node == "joinasspectator":
                    self.joinAsSpectator(attrs)

                # join room
                elif node == "joinroom":
                    ppassword = None
                    if attrs.has_key('password'):
                        ppassword = attrs['password']
                    self.joinRoom(rid = attrs['id'], publicPassword = ppassword)

                # leave room
                elif node == "leaveroom":
                    self.leaveRoom(rid = attrs['id'], attrs = attrs)

                # list users in room
                elif node == "listusers":
                    self.listUsers(rid = attrs['id'], attrs = attrs)
       
                # sending a ping ... getting a pong
                elif node == "ping":
                    self.clientSendPong()

                # Asking for room list
                elif node == "getrooms":
                    # Sending this request to the server
                    self.server.serverSendRoomsToClient(self)

                # Asking to join a room
                #elif node == "join":
                #    self.clientJoinRoom(attrs)

                # Leaving a room
                #elif node == "leave":
                #    self.clientLeaveRoom(attrs)

                # Setting a param for a room
                #elif node == "setparam":
                #    self.clientSetRoomParam(attrs)
                #

                # removing a param from a room
                #elif node == "removeparam":
                #    self.clientUnsetRoomParam(attrs)

                # adding a child room
                #elif node == "addchild":
                #    self.clientAddChildRoom(attrs)

                # Shutdown server
                #elif node == "shutdown":
                #    # Must Be root
                #    if self.isRoot:
                #        self.server.serverShutDown()

                # Kick User from entire server !!
                #elif node == "rmuser":
                #    # Must be root
                #    if attrs.has_key('nickName'):
                #        if self.isRoot:
                #            self.server.serverRmClient(attrs['nickName'],self)

                # Get Informations about a room
                #elif node == "getinfo":
                #                        # Must be root
                #    if attrs.has_key('room'):
                #        if self.isRoot:
                #            self.clientSendMessage(self.server.serverGetRoom(attrs['room']))
                                        
                # something else ?
                # TODO : Implement a method for adding simply other nodes
                else:
                    self.clientSendErrorMessage(msg="Not a known node")

            ## Si il se connect ##
            # client is connecting
            elif node == "connect":
                self.clientConnect(attrs)
            # Client should REALLY connect
            else:
                self.clientSendErrorMessage(msg="You must login first")

    def handle_close (self):
        """Client Just left without telling us (closing browser window, ...)
        """

        asynchat.async_chat.close (self)
        logging.info("Connection lost for %s(%s)" % (self.nickName, self.addr))

        # Log off from DB
        try:
            c = self.db.cursor()
            c.execute("delete from sessions where sesId = '%s'" % self.sesId)
            c.close()
            self.db.close()
        except Exception, exc:
            logging.error("Error while disconnecting from DB: %s" % ( str(exc) ))

        # On tue l'instance client
        self.close()

    def clientQuit(self):
        """Client told us he was leaving !

            Il a demand√© de partir proprement .... bravo !
        """
        # Ca marche d'autant mieux
        self.handle_close()

    def isClientInRoom(self,room):
        """Method to know if this client is in a specific room
            @room Room to test

            Permet de savoir si le client est d√©j√† dans la room X
        """

        # La room est-elle dans mon dico ?
        if self.allMyRooms.has_key(room):
            return True
        else:
            return False

    def clientAddChildRoom(self,attrs):
        """Adding a Child Room (sub-room)

            @attrs      XML attributes sent

            Permet √† un client de cr√©er une room fille
        """

        # Xml node must have parentroom and childroom attributes !!
        # which room is the mom and which is the little girl
        #
        if attrs.has_key('parentroom') and attrs.has_key('childroom'):
            thisChild = attrs['childroom']
            thisRoom = attrs['parentroom']
            # Client Must be in the parentroom
            # Client must not be in the childroom
            if self.isClientInRoom(thisRoom) and thisChild != '' and not self.isClientInRoom(thisChild):
                # Asking the server to join the room
                self.allMyRooms[thisChild] = self.server.serverAddClientToRoom(client=self,room=thisChild,parentR=thisRoom)
                # Notifying the parent room
                # (SHOULD BE IN : server.serverAddClientToRoom) BUT Problem with allMyRooms
                #
                self.allMyRooms[thisRoom].roomAddChildRoom(childR=self.allMyRooms[thisChild])

    def clientUnsetRoomParam(self,attrs):
        """Removing a room parameter

        """

        # Xml node must have a room and a name of param to remove
        if attrs.has_key('room') and attrs.has_key('name'):
            Proom = attrs['room']
            Pname = attrs['name']
            # Client must be in this room
            if self.isClientInRoom(Proom) and Proom != "" and Pname != "":
                # Notifying room
                self.allMyRooms[Proom].roomRemoveParam(name=Pname,nickName=client.nickName)


    def clientSetRoomParam(self,attrs):
        """Setting a room param

            Permet √† un client +o dans une room de changer des param√®tres
            La v√©rification du +o se passe dans la room
        """

        # Xml node must have a room and a name of param to remove and a value for the param
        if attrs.has_key('room') and attrs.has_key('name') and attrs.has_key('value'):
            Proom = attrs['room']
            Pname = attrs['name']
            Pvalue = attrs['value']
            # Client must be in this room
            if self.isClientInRoom(Proom)  and Pname != "" and Pvalue != "":
                # Notifying room
                self.allMyRooms[Proom].roomSetParam(name=Pname,value=Pvalue,nickName=self.nickName)

    def clientConnect(self, attrs):
        """Client Just sent the connect node

            <connect nickname='STR1' password='STR2'  />

        """

        try:
            nickName = self._getStrAttr('nickname', attrs)
        except InnerException, exc:
            out = "<connect msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )

        self.sesId = generateSessionId()
        password = ''

        # password ?
        if attrs.has_key('password'):
            password = attrs['password']

        # Server Must validate the nickName
        rc = self.server.isNickOk(nickName, password)
        if rc != True:
            self.clientSendErrorMessage(msg = rc[1])
            return

        # Is he authorized anyway ?
        rc, ids = self.server.isAuthorized(nickName, password, self.sesId, self.addr)
        if rc:

            # Store our own id and name
            self.ids = int(ids)
            self.name = None
            print "Our id=%d" % self.ids

            try:
                c = self.db.cursor()
                c.execute("select name from users where id = %d" % self.ids)
                rs = c.fetchone()
                if rs is None or len(rs) == 0:
                    raise InnerException(11, ERRORS[11] % self.ids)
                self.name = string.strip(rs[0])
            except Exception, exc:
                print exc

            if self.server.isBlocked(ids):
                self.clientSendErrorMessage(msg = "Client #%d is blocked" % ids)
                return

            # Is he root ?
            if self.server.isRootPass(password):
                self.isRoot = 1

            # Whoooo everything went smoothly ...
            self.loggedIn = 1
            self.nickName = nickName
            self.server.serverAddClient(self)

            # Notifying client
            self.clientSendMessage("<connect error='0' msg='Your nickname is now : %s'/>" % (nickName))

            # Old one, now we dont need to sent sesId
            #self.clientSendMessage("<connect isok='1' sesId='%s' msg='Your nickname is now : %s'/>" % (self.sesId, nickName))

            if self.isRoot:
                logging.warning("Admin connected: %s(%s)" % (self.nickName, self.addr))
            else:
                logging.info("Client connected: %s(%s)" % (self.nickName, self.addr))
        else:
            # Wrong code
            # Code should be used for database (of imap of anything) identification !
            # Some sort of non-root password
            #
            self.clientSendErrorMessage(msg = "Client not authorized or bad password")

    def inTheSameRoom(self, c, uid, rid):
        # Check that we're in the same room as recepient
        s = "select rooms_id from users_rooms where users_id in (%d, %d) and rooms_id=%d" % (self.ids, uid, rid)
        c.execute(s)
        rs = c.fetchall()

        found = False

        print 'check user in room', rs
        if rs is None or len(rs) == 0:
            pass
        else:
            if len(rs) == 2:
                found = True

        if not found:
            raise InnerException(37, ERRORS[37] % (self.ids, rid))
        # end check

    def clientHandleMessage(self, attrs):
        msgtype = int(attrs["type"])
        text = attrs["text"]

        if attrs.has_key("from_uid"):
            del attrs["from_uid"]

        try:
            if self.silent == 1:
                raise InnerException(41, ERRORS[41] % self.ids)

            c = self.db.cursor()

            if msgtype == mtypes.M_PERSONAL or msgtype == mtypes.M_PRIVATE:

                rid = self._getIntAttr("rid", attrs)
                uid = self._getIntAttr("to_uid", attrs)

                s = "select id from users where id = %d" % uid
                c.execute(s)
                rs = c.fetchone()
                if rs is None:
                    raise InnerException(6, ERRORS[6] % uid)

                s = "select id from rooms where id = %d" % rid
                c.execute(s)
                rs = c.fetchone()
                if rs is None:
                    raise InnerException(4, ERRORS[4] % rid)

                self.inTheSameRoom(c, uid, rid)

                self.server.handlePersonalMessage(self.ids, rid = rid, to_uid = uid, msgtype = msgtype, text = text, from_name = self.name)

                out = "<message error='0' uid='%d' />" 
                self.clientSendMessage(out % uid)

            elif msgtype == mtypes.M_PUBLIC:

                rid = self._getIntAttr("rid", attrs)

                s = "select id from rooms where id = %d" % rid
                c.execute(s)
                rs = c.fetchone()
                if rs is None:
                    raise InnerException(4, ERRORS[4] % rid)
                self.server.handlePersonalMessage(self.ids, rid = rid, msgtype = msgtype, text = text, from_name = self.name)

                self.inTheSameRoom(c, uid, rid)

                out = "<message error='0' rid='%d' />" 
                self.clientSendMessage(out % (rid))
            elif msgtype == mtypes.M_BROADCAST:
                    self.server.handlePersonalMessage(self.ids, msgtype = msgtype, text = text, from_name = self.name)

                    out = "<message error='0' />" 
                    self.clientSendMessage(out)
            else:
                raise InnerException(16, ERRORS[16] % msgtype)

        except InnerException, exc:
            out = "<message msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
        except Exception, exc:
            out = "<message error='-1' msg=%s />" 
            self.clientSendMessage( out % (Q(str(exc))) )
        
    def sendCustomMessage(self, attrs):

        out = []
        if attrs.has_key("from_uid"):
            out.append("from_uid='%d'" % attrs["from_uid"])
        if attrs.has_key("to_uid"):
            out.append("to_uid='%d'" % attrs["to_uid"])
        if attrs.has_key("type"):
            out.append("type='%d'" % attrs["type"])
        if attrs.has_key("text"):
            out.append("text=%s" % Q(attrs["text"]))
        if attrs.has_key("from_name"):
            out.append("from_name=%s" % Q(attrs["from_name"]))
        if attrs.has_key("rid"):
            out.append("rid='%d'" % attrs["rid"])

        # D 425

        import time
        t = time.gmtime()
        tm = "%04d%02d%02d%02d%02d%02d" % (t[0], t[1], t[2], t[3], t[4], t[5])
        out.append("time='%s'" % tm)
        msg = """
        <message %s
        />
        """ % " ".join(out)

        print msg
        self.clientSendMessage(msg)

    def _clientHandleMessage(self,attrs,texte):
        """Method to handle classic text messages

            @attrs[back OR b]   Should we send the message back to the user (room messages only)?


            Cette m√©thode g√®re les messages classiques
            priv√©s ou vers une room
            Client : <msg toclient='STR1'>STR2</msg> OU SHORT VERSION <m c='XXX'>YYY</m>
            Room   : <msg toroom='STR1' back='BOOL1'>STR2</msg> OU SHORT VERSION <m r='STR1' b='BOOL1'>YYY</m>

        """

        # back d√©finit dans le cas d'un message √† une room si il souhaite √©galement recevoir ce message en retour
        # Should we send the message back to the user (room messages only)?
        back = "0"
        if attrs.has_key('back'):
            back = attrs['back']
        elif attrs.has_key('b'):
            back = attrs['b']

        # Private Message
        # Un message prive
        if attrs.has_key('toclient'):
            # Asking the server to send the message to other client
            self.server.serverSendMessageToClient(data=texte,sender=self.nickName, dest=attrs['toclient'])
        # Short Version
        elif attrs.has_key('c'):
            self.server.serverSendMessageToClient(data=texte,sender=self.nickName, dest=attrs['c'])


        # Un message dans une room
        # Room message
        elif attrs.has_key('toroom'):
            self.clientSendToRoom(data=texte,room=attrs['toroom'],back=back)
        # Short Version
        elif attrs.has_key('r'):
            self.clientSendToRoom(data=texte,room=attrs['r'],back=back)


        # Un message a tout le monde
        # Broadcast Message to everyone
        # Must Be root
        elif attrs.has_key('broadcast'):
            if self.isRoot:
                self.server.serverSendToAllClients(data=texte,sender=self.nickName)

        # Sinon Ya un probl√®me on sait pas ou l'envoyer
        # Not a good message node, not enough information
        else:
            self.clientSendErrorMessage(msg="No recipient given")




    def clientSendPong(self):
        """Asking a ping getting a pong ...
            Si on recoit un ping
            on envoit un pong
            <ping />
        """

        # C'est plutot basique
        # pretty simple
        self.clientSendMessage("<pong />")

    def clientSendToRoom(self,data,room,back):
        """Sending message to a room

            @data   The message
            @room   The room
            @back   Should we send the message back ?


            On envoit un message dans une room
        """

        # suis je dedans ?
        # Client must be in room
        if self.isClientInRoom(room):
            # Alors on envoit ... go go go
            # Asking the room to send the message
            self.allMyRooms[room].roomSendToAllClients(msg=data,nickName=self.nickName,back=back)
        else:
            # Booooooo
            self.clientSendErrorMessage(msg="No room by that name")

    def close (self):
        """Client Left the server
            Quand le client vient de se d√©connecter
        """

        # Debug information
        logging.info("Disconnect requested by %s(%s)" % (self.nickName, self.addr))

        # Notifying Server
        self.server.serverClientQuit(nickName = self.nickName, uid = self.ids)

        # En fait non on le fait l√† ... c'est bizarre ?
        # .... hum ....
        if self.server.allNickNames.has_key(self.nickName):
            del self.server.allNickNames[self.nickName]

        # Ca on est d√©j√† cens√© l'avoir fait ...
        asynchat.async_chat.close (self)

    def clientSendMessage (self, msg):
        """Method to send an XML message to this client
            M√©thode d'envoi d'un message au client
            le message doit d√©j√† √™tre format√© en XML
        """

        msg = "%s%s" % (msg, self.terminator)

        try:
            self.push(msg)
        except:
            logging.debug("Failed to send message to %s(%s)" % (self.nickName, self.addr))

    def clientSendErrorMessage(self, msg):
        """Error message
            Permet de formater un message en XML indiquant au client qu'une erreur s'est produite
            Passer uniquement le texte de l'erreur
        """

        self.clientSendMessage("<error>%s</error>" % msg)



    def clientSendInfoMessage(self, msg):
        """Info message
            Permet de formater un message en XML indiquant au client qu'une erreur s'est produite
            Passer uniquement le texte de l'erreur
        """

        self.clientSendMessage("<info>%s</info>" % msg)



    def clientLeaveRoom(self, attrs):
        """Client leaves a room
            Le client quitte une room
            <leave room='STR1' />
        """

        # Ya t'il le bon param√®tre ?
        # XML must have a room param
        if attrs.has_key('room'):
            room = attrs['room']
            # Est-il bien dans cette room (Si oui c'est qu'elle existe)
            # Client Must be in the room
            if self.isClientInRoom(room):
                # On informe la room
                # Notifying room

                self.allMyRooms[room].roomRemoveClient(nickName=self.nickName)

                # On la suprime
                # deleting the room
                del self.allMyRooms[room]
                # On informe le client que c'est OK
                # Notifying client
                self.clientSendMessage(msg="<leaved room='%s' />" % room)
            else:
                # arf t'es pas d'dans
                self.clientSendErrorMessage(msg="Not a known room")

        # Si pas de bon param√®tre ... on fait rien
        else:
            self.clientSendErrorMessage(msg="No room specified")


    def clientSendHelp(self):
        """
            Liste des param√®tres possibles
            √† documenter
        """

        # A faire , A faire , A faire , A faire , A faire , A faire , A faire , A faire , A faire , ...
        self.clientSendMessage("<help><![[CDATA][First of all send a <connect nickname='XYZ' /> node]]></help>")

