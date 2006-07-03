# -*- coding: utf-8 -*-

import socket
import asynchat
import xml.dom.minidom as xmldom
import xml.sax.saxutils as SAX
import string

from traceback import *

from palabre import config, logging, version, escape_string

if config.get("database", "type") == "mysql":
    import MySQLdb as DB
elif config.get("database", "type") == "firebird":
    import kinterbasdb as DB
else:
    raise Exception("Unknown database type in config")
 

def Q(v):
    """ Shortcut for saxutils.quoteattr """
    return SAX.quoteattr(v)

def safeClose(c):
    """ Close cursor, safely, quietly """
    try:
        c.close()
    except Exception, exc:
        print str(exc)
        pass

_roomTemplate = '''
                <room id='%d' 
                        name=%s

                        creatorid='%d'
                        operatorid='%d'

                        allowedUsers='%d'
                        languageid='%d'
                        temporary='%d'
                        passwordProtected='%d'

                        moderationAllowed='%d'
                        roomManagementLevel='%d'
                        userManagementlevel='%d'

                        numberOfUsers='%d'
                        numberOfSpectators='%d'
                />
'''

_roomQuery = '''
            select
                id,
                name,

                creatorid,
                operatorid,

                allowedUsers,
                languageid,
                temporary,
                passwordProtected,

                moderationAllowed,
                roomManagementLevel,
                userManagementlevel,

                numberOfUsers,
                numberOfSpectators

            from rooms %s order by name 
'''

class PalabreClient(asynchat.async_chat):

    def __init__(self,server, conn, addr, db):

        # Asynchat initialisation ... (main class for sending and receiving messages */
        asynchat.async_chat.__init__ (self, conn)

        self.server = server
        self.conn = conn

        # Database connection
        self.db = db

        # Adresse Ip ?
        self.addr = addr[0]

        # Null character
        self.carTerm = "\0"

        # Inherited from asynchat ..
        self.set_terminator (self.carTerm)

        # String de réception des données
        self.data = ""

        # Nickname vide tant qu'on a pas recu la balise nickname
        self.nickName = ""

        # Donc on est pas encore logué
        self.loggedIn = 0

        # Liste des rooms où le client est connecté
        self.allMyRooms = {}

        # A t'il fournit le mot magique ?
        self.isRoot = 0

        logging.info("Connection initialized for %s" % self.addr)

    def listGroups(self, sesId = None):
        print 'listing groups...'
        out = "<groups isOk='0' msg=%s />"
        try:
            c = self.db.cursor()
            c.execute("select id, name, mlevel from groups order by name")
            rs = c.fetchall()

            out = ["<groups isOk='1'>"]
            for r in rs:
                print r
                out.append("<group id='%d' name=%s moderationLevel='%d' />" %\
                    (r[0], Q(string.strip(r[1])), r[2]))
                print out
            out.append("</groups>")
            self.clientSendMessage("\n".join(out))
        except Exception, exc:
            self.clientSendMessage( out % Q(str(exc)) )

    def createGroup(self, sesId = None, name = None, moderationLevel = None):
        print 'creating group...', name, moderationLevel

        out = "<creategroup isOk='0' msg=%s />"
        try:
            c = self.db.cursor()
            c.execute("insert into groups (name, mlevel) values ('%s', %d)" %\
                (escape_string(name), int(moderationLevel)))
            c.execute("select id, name, mlevel from groups where name = '%s' and mlevel='%d'" %\
                (escape_string(name), int(moderationLevel)))

            r = c.fetchone()

            out = ["<creategroup isOk='1'>"] 
            out.append("<group id='%d' name='%s' moderationLevel='%d' />" %\
                    (r[0], escape_string(string.strip(r[1])), r[2]))
            out.append("</creategroup>")
            self.clientSendMessage("\n".join(out))
        except Exception, exc:
            self.clientSendMessage( out % Q(str(exc)) )

    def getGroupProperties(self, sesId = None, gid = None):
        print 'retrieving group properties...', gid

        try:
            c = self.db.cursor()
            c.execute("select id, name, mlevel from groups where id='%d'" % int(gid))

            r = c.fetchone()
            if r is None:
                raise Exception("Can't find group with id='%d'" % int(gid))

            out = "<getgroupproperties isOk='1' id='%d' name='%s' moderationLevel='%d' />" %\
                (r[0], escape_string(string.strip(r[1])), r[2])
            self.clientSendMessage(out)
        except Exception, exc:
            out = "<getgroupproperties isOk='0' id='%d' msg=%s />"
            self.clientSendMessage( out % ( int(gid), Q(str(exc)) ) )

    def setGroupProperties(self, sesId = None, gid = None, name = None, moderationLevel = None):
        print 'retrieving group properties...', gid

        out = "<setgroupproperties isOk='0' msg=%s />"
        try:
            c = self.db.cursor()

            c.execute("select id, name, mlevel from groups where id='%d'" % int(gid))

            r = c.fetchone()
            if r is None:
                raise Exception("Can't find group with id='%d'" % int(gid))

            s = 'update groups set '
            if name is not None:
                s += " name = '%s' " % escape_string(name)
            if moderationLevel is not None:
                s += " mlevel = %d " % int(moderationLevel)
            s += ' where id = %d' % int(gid)

            c.execute(s)

            out = "<setgroupproperties isOk='1' id='%d' />" % int(gid)
            self.clientSendMessage(out)
        except Exception, exc:
            self.clientSendMessage( out % Q(str(exc)) )

    def listMembers(self, sesId = None, gid = None):
        print 'retrieving group members...', gid

        try:
            c = self.db.cursor()
            s = 'select u.id, u.name from users u where gid = %d' % int(gid)
            c.execute(s)

            out = ["<listmembers isOk='1' id='%d' >" % int(gid)]

            rs = c.fetchall()
            for r in rs:
                out.append("<client id='%d' name=%s />" %\
                    (r[0], Q(string.strip(r[1]))) )

            out.append("</listmembers>");
 
            self.clientSendMessage("\n".join(out))
        except Exception, exc:
            out = "<listmembers isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def getUserProperties(self, sesId = None, uid = None):
        print 'retrieving user properties... %d' % int(uid)

        try:
            c = self.db.cursor()
            s = ''' select u.id, u.name, u.gid, u.languageid, u.isblocked
                from users u where id = %d ''' % int(uid)
            c.execute(s)

            out = ["<getuserproperties isOk='1' id='%d' >" % int(uid)]

            rs = c.fetchall()
            if len(rs) == 0:
                raise Exception("Can't find client with id='%d'" % int(uid))

            for r in rs:
                out.append("<client id='%d' name=%s groupid='%d' languageid='%d' isblocked='%d' />" %\
                    (r[0], Q(string.strip(r[1])), r[2], r[3], r[4])
                )

            out.append("</getuserproperties>");
 
            self.clientSendMessage("\n".join(out))
        except Exception, exc:
            out = "<getuserproperties isOk='0' id='%d' msg=%s />" 
            self.clientSendMessage( out % ( int(uid), Q(str(exc)) ) )

    def setUserProperties(self, sesId = None, attrs = {}):
        uid = int(attrs['id'])
        del attrs['id']

        print 'setting user properties... %d' % int(uid)

        c = None
        try:
            c = self.db.cursor()

            c.execute("select id from users where id='%d'" % int(uid))

            r = c.fetchone()
            if r is None:
                raise Exception("Can't find user with id='%d'" % int(uid))

            s = 'update users set '

            if attrs.has_key('name'):
                s += " name = %s " % escape_string(attrs['name'])
            if attrs.has_key('languageid'):
                s += " languageid = '%d' " % int(attrs['languageid'])
            if attrs.has_key('password'):
                s += " password = %s " % escape_string(attrs['password'])
            if attrs.has_key('groupid'):
                s += " gid = '%d' " % int(attrs['groupid'])
            if attrs.has_key('isblocked'):
                s += " isblocked = '%d' " % int(attrs['isblocked'])
   
            s += ' where id = %d' % int(uid)
            c.execute(s)

            out = "<setuserproperties isOk='1' id='%d' />" % int(uid)
            self.clientSendMessage(out)
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<setuserproperties isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def getRoomList(self, sesId = None):
        print 'retrieving room list...'

        c = None
        try:
            c = self.db.cursor()

            # Pass empty parameter
            s = _roomQuery % ""

            c.execute(s)

            out = ["<getroomlist isOk='1' >"]

            rs = c.fetchall()
            for r in rs:
                out.append(_roomTemplate %\
                    (r[0], Q(string.strip(r[1])), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12])
                )

            out.append("</getroomlist>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<getroomlist isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def getRoomProperties(self, sesId = None, rid = None):
        print 'retrieving room properties...'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            # Pass where clause
            s = _roomQuery % ("where id = %d" % rid)
            print s

            c.execute(s)

            out = ["<getroomproperties isOk='1' >"]

            rs = c.fetchall()
            for r in rs:
                out.append(_roomTemplate %\
                    (r[0], Q(string.strip(r[1])), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12])
                )

            out.append("</getroomproperties>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<getroomproperties isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def setRoomProperties(self, sesId = None, rid = None, attrs = {}):
        print 'setting room properties...'

        rid = int(rid)
        c = None

        try:
            print attrs
            c = self.db.cursor()

            c.execute("select id from rooms where id='%d'" % int(rid))

            r = c.fetchone()
            if r is None:
                raise Exception("Can't find room with id='%d'" % int(rid))

            s = 'update rooms set '

            if attrs.has_key('name'):
                s += " name = %s " % escape_string(attrs['name'])
            if attrs.has_key('languageid'):
                s += " languageid = '%d' " % int(attrs['languageid'])
            if attrs.has_key('pvtPassword'):
                s += " pvtpassword = %s " % escape_string(attrs['pvtPassword'])
            if attrs.has_key('publicPassword'):
                s += " publicpassword = %s " % escape_string(attrs['publicPassword'])
            if attrs.has_key('temporary'):
                s += " temporary = '%d' " % int(attrs['temporary'])
            if attrs.has_key('allowedUsers'):
                s += " allowedUsers = '%d' " % int(attrs['allowedUsers'])
            if attrs.has_key('passwordProtected'):
                s += " passwordProtected = '%d' " % int(attrs['passwordProtected'])
            if attrs.has_key('moderationAllowed'):
                s += " moderationAllowed = '%d' " % int(attrs['moderationAllowed'])
            if attrs.has_key('roomManagementLevel'):
                s += " roomManagementLevel = '%d' " % int(attrs['roomManagementLevel'])
            if attrs.has_key('userManagementlevel'):
                s += " userManagementlevel = '%d' " % int(attrs['userManagementlevel'])
      
            s += ' where id = %d' % int(rid)
            print s
 
            c.execute(s)

            out = ["<setroomproperties isOk='1' >"]
            out.append("</setroomproperties>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<setroomproperties isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def removeAllowedUser(self, sesId = None, rid = None, uid = None):
        print 'removing allowed user'

        rid = int(rid)
        uid = int(uid)
        c = None

        try:
            c = self.db.cursor()
            s = ''

            raise Exception("Not implemented yet")
            print s
 
            c.execute(s)

            out = ["<removealloweduser isOk='1' >"]
            out.append("</removealloweduser>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<removealloweduser isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )
 
    def appendNewAllowedUser(self, sesId = None, rid = None, uid = None):
        print 'adding new allowed user'

        rid = int(rid)
        uid = int(uid)
        c = None

        try:
            c = self.db.cursor()
            s = ''

            raise Exception("Not implemented yet")
            print s
 
            c.execute(s)

            out = ["<addnewalloweduser isOk='1' >"]
            out.append("</addnewalloweduser>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<addnewalloweduser isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def inviteUser(self, sesId = None, rid = None, uid = None):
        print 'inviting user'

        rid = int(rid)
        uid = int(uid)
        c = None

        try:
            c = self.db.cursor()
            s = ''

            raise Exception("Not implemented yet")
            print s
 
            c.execute(s)

            out = ["<inviteuser isOk='1' >"]
            out.append("</inviteuser>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<inviteuser isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def createRoom(self, sesId = None, attrs = {}):
        print 'creating new room'

        c = None

        try:
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
                    raise Exception("Room with name '%s' already exists" % attrs['name'])

            #

            keys = []
            s = []

            if attrs.has_key('name'):
                s.append( " '%s' " % escape_string(attrs['name']))
                keys.append("name")

            if attrs.has_key('languageid'):
                s.append(" '%d' " % int(attrs['languageid']))
                keys.append("languageid")

            if attrs.has_key('pvtPassword'):
                s.append( " '%s' " % escape_string(attrs['pvtPassword']))
                keys.append("pvtPassword")

            if attrs.has_key('publicPassword'):
                s.append( " '%s' " % escape_string(attrs['publicPassword']))
                keys.append("publicPassword")
 
            if attrs.has_key('temporary'):
                s.append(" '%d' " % int(attrs['temporary']))
                keys.append("temporary")

            if attrs.has_key('allowedUsers'):
                s.append(" '%d' " % int(attrs['allowedUsers']))
                keys.append("allowedUsers")

            if attrs.has_key('passwordProtected'):
                s.append(" '%d' " % int(attrs['passwordProtected']))
                keys.append("passwordProtected")

            if attrs.has_key('moderationAllowed'):
                s.append(" '%d' " % int(attrs['moderationAllowed']))
                keys.append("moderationAllowed")

            if attrs.has_key('roomManagementLevel'):
                s.append(" '%d' " % int(attrs['roomManagementLevel']))
                keys.append("roomManagementLevel")

            if attrs.has_key('userManagementlevel'):
                s.append(" '%d' " % int(attrs['userManagementlevel']))
                keys.append("userManagementlevel")

            s = "insert into rooms (%s) values (%s)" %\
                (",".join(keys), ",".join(s))

            self.db.commit()

            print s
            self.db.begin()
            self.db.execute_immediate(s)
            self.db.commit()
            print 'executed'

            out = ["<createroom isOk='1' name=%s >" % Q(attrs['name'])]
            out.append("</createroom>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<createroom isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def delRoom(self, sesId = None, rid = None):
        print 'delete room'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            c.execute("select id from rooms where id='%d'" % int(rid))

            r = c.fetchone()
            if r is None:
                raise Exception("Can't find room with id='%d'" % int(rid))

            s = 'delete from rooms where id = %d' % rid

            print s
 
            c.execute(s)

            out = ["<delroom isOk='1' id='%d' >" % rid]
            out.append("</delroom>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<delroom isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def joinRoom(self, sesId = None, rid = None, publicPassword = None):
        print 'joining room'

        rid = int(rid)
        c = None

        try:
            c = self.db.cursor()

            print 'Client #%d attepting to join room #%d' % (self.ids, rid)

            #s = "update users_rooms"
            s = "select name from rooms where id = %d" % rid
            print s
            c.execute(s)
            r = c.fetchone()
            if r is None:
                raise Exception("Can't find room with id='%d'" % int(rid))

            s = "select rooms_id from users_rooms where users_id = %d" % self.ids
            print s
            c.execute(s)

            rs = c.fetchall()
            for r in rs:
                print 'Client #%d now in room #%d' % (self.ids, int(r[0]))
                if int(r[0]) == rid:
                    raise Exception('Client #%d already in room #%d' % (self.ids, rid))

            self.db.commit()
            self.db.begin()
            self.db.execute_immediate("insert into users_rooms (users_id, rooms_id) values (%d, %d)" % (self.ids, rid))
            self.db.commit()
 
            out = "<joinroom isOk='1' uid='%d' rid='%d' />" % (self.ids, rid)
 
            self.clientSendMessage(out)
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<joinroom isOk='0' msg=%s />" 
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
                raise Exception("Can't find room with id='%d'" % int(rid))

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
                raise Exception("Client #%d not in room #%d" % (self.ids, int(rid)))

            self.db.commit()
            self.db.begin()
            self.db.execute_immediate("delete from users_rooms where users_id = %d and rooms_id = %d" % (self.ids, rid))
            self.db.commit()
 
            out = "<leaveroom isOk='1' uid='%d' rid='%d' />" % (self.ids, rid)
 
            self.clientSendMessage(out)
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<leaveroom isOk='0' rid='%d' msg=%s />" 
            self.clientSendMessage( out % (rid, Q(str(exc))) )

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
                raise Exception("Can't find room with id='%d'" % int(rid))

            s = "select id, name from users where id in (select users_id from users_rooms where rooms_id = %d)" % rid
            print s

            c.execute(s)

            out = ["<listusers isOk='1' >"]

            rs = c.fetchall()
            for r in rs:
                out.append("<client id='%d' name='%s' />" %\
                    (r[0], escape_string(string.strip(r[1])))
                )

            out.append("</listusers>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<listusers isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

                     
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

                # He is sending a message
                if node == "msg" or node == "m":
                    self.clientHandleMessage(attrs,texte)

                # list groups
                elif node == "listgroups":
                    self.listGroups()

                # create group
                elif node == "creategroup":
                    self.createGroup(name = attrs["name"], moderationLevel = attrs["moderationLevel"])

                # get group properties
                elif node == "getgroupproperties":
                    self.getGroupProperties(gid = attrs["id"])

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
                    self.createRoom(attrs = attrs)

                # delete room
                elif node == "delroom":
                    self.delRoom(rid = attrs['id'])

                # join room
                elif node == "joinroom":
                    publicPassword = None
                    if attrs.has_key('publicPassword'):
                        publicPassword = attrs['publicPassword']
                    self.joinRoom(rid = attrs['id'], publicPassword = publicPassword)

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
                elif node == "join":
                    self.clientJoinRoom(attrs)

                # Leaving a room
                elif node == "leave":
                    self.clientLeaveRoom(attrs)

                # Setting a param for a room
                elif node == "setparam":

                    self.clientSetRoomParam(attrs)

                # removing a param from a room
                elif node == "removeparam":
                    self.clientUnsetRoomParam(attrs)

                # adding a child room
                elif node == "addchild":
                    self.clientAddChildRoom(attrs)

                # Shutdown server
                elif node == "shutdown":
                    # Must Be root
                    if self.isRoot:
                        self.server.serverShutDown()
                # Kick User from entire server !!
                elif node == "rmuser":
                    # Must be root
                    if attrs.has_key('nickName'):
                        if self.isRoot:
                            self.server.serverRmClient(attrs['nickName'],self)

                # Get Informations about a room
                elif node == "getinfo":
                                        # Must be root
                    if attrs.has_key('room'):
                        if self.isRoot:
                            self.clientSendMessage(self.server.serverGetRoom(attrs['room']))
                                        
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
            Le client vient de se déconnecter ... 'ala' goret surement
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

            Il a demandé de partir proprement .... bravo !
        """
        # Ca marche d'autant mieux
        self.handle_close()

    def isClientInRoom(self,room):
        """Method to know if this client is in a specific room
            @room Room to test

            Permet de savoir si le client est déjà dans la room X
        """

        # La room est-elle dans mon dico ?
        if self.allMyRooms.has_key(room):
            return True
        else:
            return False

    def clientAddChildRoom(self,attrs):
        """Adding a Child Room (sub-room)

            @attrs      XML attributes sent

            Permet à un client de créer une room fille
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

            Permet à un client +o dans une room de changer des paramètres
            La vérification du +o se passe dans la room
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

            Le client envoit une node 'connect'
            On vérifie s'il a un password, un code ...
            On appelle la fonction de vérification éventuellement

        """

        # Needs a nickname
        if not attrs.has_key('nickname'):
            self.clientSendErrorMessage(msg = "No NickName Attribute")
            return
        # Needs a session Id
        if not attrs.has_key('sesId'):
            self.clientSendErrorMessage(msg = "No Session Id Attribute")
            return
 
        nickName = attrs['nickname']
        self.sesId = attrs['sesId']
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
        rc, ids = self.server.isAuthorized(nickName, password, self.sesId)
        if rc:

            # Store our own id
            self.ids = int(ids)
            print "Our id=%d" % self.ids

            # Is he root ?
            if self.server.isRootPass(password):
                self.isRoot = 1

            # Whoooo everything went smoothly ...
            self.loggedIn = 1
            self.nickName = nickName
            self.server.serverAddClient(self)

            # Notifying client
            self.clientSendMessage("<connect isok='1' msg='Your nickname is now : %s'/>" % nickName)

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

    def clientJoinRoom(self,attrs):
        """
            Clients joins a room

            Le client décide de rejoindre une room
            Méthode appellée par parseData
            <join room='XXX' />
        """

        # Xml node must have a room param
        if attrs.has_key('room'):
            room = attrs['room']
            # Est-il déjà dans cette room ?
            #Client must not be in the room
            if self.isClientInRoom(room):
                # Si oui c'est tant pis ....
                self.clientSendErrorMessage(msg="You are already in this room")
            else:
                # Asking server to join the room
                # The server returns the room instance

                # Sinon on l'ajoute à la liste
                self.allMyRooms[room] = self.server.serverAddClientToRoom(self,room)


        else:
            self.clientSendErrorMessage(msg="No room specified")



    def clientHandleMessage(self,attrs,texte):
        """Method to handle classic text messages

            @attrs[back OR b]   Should we send the message back to the user (room messages only)?


            Cette méthode gère les messages classiques
            privés ou vers une room
            Client : <msg toclient='STR1'>STR2</msg> OU SHORT VERSION <m c='XXX'>YYY</m>
            Room   : <msg toroom='STR1' back='BOOL1'>STR2</msg> OU SHORT VERSION <m r='STR1' b='BOOL1'>YYY</m>

        """

        # back définit dans le cas d'un message à une room si il souhaite également recevoir ce message en retour
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

        # Sinon Ya un problème on sait pas ou l'envoyer
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
            Quand le client vient de se déconnecter
        """

        # Debug information
        logging.info("Disconnect requested by %s(%s)" % (self.nickName, self.addr))

        # Notifying Server
        self.server.serverClientQuit(nickName = self.nickName, uid = self.ids)

        # En fait non on le fait là ... c'est bizarre ?
        # .... hum ....
        if self.server.allNickNames.has_key(self.nickName):
            del self.server.allNickNames[self.nickName]

        # Ca on est déjà censé l'avoir fait ...
        asynchat.async_chat.close (self)

    def clientSendMessage (self, msg):
        """Method to send an XML message to this client
            Méthode d'envoi d'un message au client
            le message doit déjà être formaté en XML
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

        # Ya t'il le bon paramètre ?
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

        # Si pas de bon paramètre ... on fait rien
        else:
            self.clientSendErrorMessage(msg="No room specified")


    def clientSendHelp(self):
        """
            Liste des paramètres possibles
            à documenter
        """

        # A faire , A faire , A faire , A faire , A faire , A faire , A faire , A faire , A faire , ...
        self.clientSendMessage("<help><![[CDATA][First of all send a <connect nickname='XYZ' /> node]]></help>")

