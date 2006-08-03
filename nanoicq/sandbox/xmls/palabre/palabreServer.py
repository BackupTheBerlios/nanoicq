#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import asyncore
import string
import signal
import sys
import os
import sys
import time
import threading

from palabre import config, logging, version, escape_string
#from util import generateSessionId, safeClose
from util import *
from Message import mtypes

SilentCheckInterval = 3 # seconds

DB_MYSQL    = 0
DB_FIRE     = 1
dbtype = -1


if config.get("database", "type") == "mysql":
    import MySQLdb as DB
    dbtype = DB_MYSQL
elif config.get("database", "type") == "firebird":
    import kinterbasdb as DB
    dbtype = DB_FIRE
else:
    raise Exception("Unknown database type in config")

from datetime import datetime

from palabreClient import PalabreClient
from palabreRoom import PalabreRoom



class PalabreServer(asyncore.dispatcher):
    channel_class = PalabreClient

    def __init__(self, HOST='', PORT=2468, rootPassword=''):
        """ Constructor of the server

        Defines many variables

        @HOST = Which Adress to listen to, Default : listens on all available interfaces
        @PORT = Which Port to listen on, Default : 50007
        @rootPassword = Defines the root password, to administrate the server (shutdown, ...)

        <Returns nothing"""

        # Version
        self.version = version

        # Root password
        self.rootPassword = rootPassword

        # Connection informations
        self.HOST = HOST
        self.PORT = PORT

        # Connected clients and available rooms
        self.allNickNames = {}
        self.allRooms = {}

        # DB connection flag
        self.dbOk = False

        try:
            asyncore.dispatcher.__init__(self)

            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind((self.HOST, self.PORT))
            self.listen(5)
        except:
            logging.error("Error while starting: Network address and port already in use ?")
            sys.exit()

        if self.HOST == "":
            showHost = "All interfaces"
        else:
            showHost = self.HOST


        logging.info("Running on: %s" % showHost)
        logging.info("Port: %s" % self.PORT)

        self.db = self.connectToDb()
        if self.db is None:
            self.serverShutDown()

        self.timer = threading.Thread(target = self.timerThread, args=(self,))
        self.timer.start()

    def timerThread(self, arg):
        while True:
            time.sleep(SilentCheckInterval)
            self.checkSilentUsers()

    def checkSilentUsers(self):
        for ii in self._map:
            try:
                if self._map[ii].silent == 1:
                    gap = time.time() - self._map[ii].silentStart
                    print 'GAP>', gap, self._map[ii].silentPeriod
                    if gap >= self._map[ii].silentPeriod:
                        print "Removing silent flag from user %d" % self._map[ii].ids
                        self._map[ii].silent = 0
            except AttributeError:
                pass

    def checkDbStatus(self, db):
        checkTables = ['users']

        c = db.cursor()
        for t in checkTables:
            c.execute("select * from %s where 1=2" % t)

        self.dbOk = True
        return True       

    def connectToDb(self):
        """
        """
        # FIXME:
        # set-variable=max_connections=500
        # set-variable=wait_timeout=200

        logging.debug("Connecting to database...")
        db = None

        try:
            if config.get("database", "type") == "mysql":
                logging.debug("Using MySQL driver")
                db = DB.connect(
                    host = config.get("database", "host"),
                    port = config.getint("database", "port"), 
                    user = config.get("database", "user"), 
                    passwd = config.get("database", "password"), 
                    db = config.get("database", "database") )
            else:
                logging.debug("Using Firebird driver")
                db = DB.connect(
                    host = config.get("database", "host"),
                    user = config.get("database", "user"), 
                    password = config.get("database", "password"), 
                    database = config.get("database", "database") )
 
            self.checkDbStatus(db)

            logging.debug("Connected to database")
        except DB.DatabaseError, exc:
            logging.error("DB connection: " + str(exc))

        return db

    def handle_accept(self):
        """Handle incoming connections
        Defines class variable channel_class
        """
        conn, addr = self.accept()
        connector = self.channel_class(self, conn, addr, self.connectToDb())

    def handle_close(self):
        """When shuting down the server
        Closes log file
        Shutdown the server
        """
        self.logFile.close()
        self.serverShutDown()

    def writable(self):
        return 0

    def serverShutDown(self, reason = ''):
        """When asked to shutdown the server by root
        """

        logging.warning("Server shutdown requested")

        """ On envoit un message à tous les clients """

        if reason != '':
            reason = "(%s) " % reason

        for p in self.allNickNames.values():
            p.clientSendErrorMessage(
                msg = "### Server is now going down %s... ###" % reason)
            p.close()

        self.close()
        # !!!!DIRTY HACK ALERT!!!!
        # we have to find another way to do this
        # os._exit is indeed a very dirty hack and should not be used at all.
        # indeed i suck and don't understand much of what i do
        # the previous comment and its poor english was graciously 
        # brougth to you by lekma
        # indeed (i am so f***ing tired and it's only 20:13)
        os._exit(0)

    def serverClientExists(self, nickName):
        """Method to know if a user exists and is connected
            @nickName : nickName to test
        """

        if nickName != "" and self.allNickNames.has_key(nickName):
            if isinstance(self.allNickNames[nickName], PalabreClient):
                return True

        return False

    def serverRmClient(self, nickName, rootUser):
        """Method to handle a kick off
            @nickName : Client to kick !
            @rootUser : Root user who asked for the kick

        """

        if self.serverClientExists(nickName):
            self.allNickNames[nickName].clientSendErrorMessage("You have been kicked from the server by an administrator")
            self.allNickNames[nickName].clientQuit()
            rootUser.clientSendInfoMessage("Client %s kicked" % nickName);
        else:
            rootUser.clientSendErrorMessage("No user connected with nickname: %s" % nickName);


    def serverClientQuit(self, nickName, uid = None):
        """Method to handle a client deconnection
        @nickName : Nickname of the client to disconnect.
        <Returns nothing"""

        if uid is not None:
            self.setLastIP(uid)
            self._clientLeft(uid)
            self.leaveAllRooms(uid)

        logging.info("Client left: %s" % nickName)

        # Check if it really exists
        if nickName != "" and self.allNickNames.has_key(nickName):
            del self.allNickNames[nickName]

        # Notify every rooms
        # We should only notify its rooms,
        # But PalabreClient Instance might already be detroyed
        # So we lost all informations ....
        for p in self.allRooms.values():
            p.roomRemoveClient(nickName)

    def _showSessions(self):
        c = self.db.cursor()

        print "="*40
        s = "select id, sesid from sessions order by id"
        c.execute(s)

        rs = c.fetchall()
        if rs is not None:
            for r in rs:
                print r

        self.db.commit()

    def _clientLeft(self, uid):
        self.db.commit()

        self._showSessions()

        self.db.begin()
        c = self.db.cursor()
        s = "select id, sesid from sessions where userid = %d" % uid
        c.execute(s)

        rs = c.fetchone()
        if rs is None:
            logging.error("Disconnect was requested by user which does not have associated session (id='%d', sesId='unknown')" % (uid))
            return

        s = "delete from sessions where id = %d" % int(rs[0])
        c.execute(s)
        self.db.commit()

        self._showSessions()

        logging.info("User #%d successfully logged off" % uid)

    def serverSendToClientByName(self, nickName, msg, type):
        """ Method to send a message to ONE specific clients

        @nickName Nickname of the client
        @msg Body of the message to send
        @type Type = "error" ? or classic message.

        Then passes the message to client Instance via clientSendErrorMessage() or clientSendMessage()

        <Returns nothing"""

        # Client Nickname must exist
        if self.allNickNames.has_key(nickName):

            # Un client peut envoyer un messsage d'erreur ? à vérifier
            if type == "error":
                self.allNickNames[nickName].clientSendErrorMessage(msg)
            else:
                self.allNickNames[nickName].clientSendMessage(msg)

    def serverSendMessageToClient(self, data, sender, dest):
        """ Method to send a message from a client to another (private message)
        @data : Body of the message to send
        @sender : Nickname of the sender
        @dest : nickName of the recipient

        <returns Nothing """

        # Si le sender existe ainsi que le destinataire c'est ok
        # Normalement le sender existe puisque cette méthode est appellée par une instance client

        # Sender and recipient must exists
        if self.allNickNames.has_key(sender) and self.allNickNames.has_key(dest):
            self.allNickNames[dest].clientSendMessage(msg = "<m f='%s'>%s</m>" % (sender, data))

    def serverSendToAllClients(self, data, sender):
        """ Method to broadcast a message to everyone
         @data : Message to broadcast
         @sender : Sender of the message

         Should be only a method for "root"
        """
        # Creating message
        data = "<m f='%s'>%s</m>" % (sender, data)

        # Sending to everyone
        for p in self.allNickNames.values():
            p.clientSendMessage(msg=data)

    def serverSendAdminMessage(self, msg):
        """ Broadcast a technical Message
         @msg Message to send
        """

        # Admin rulez ... Broadcast everything
        for p in self.allNickNames.values():
            p.clientSendMessage(msg=data)

    def serverSendToRoom(self, data, sender, room, back):
        """ Method to send a message from a client to a specific room

         @data Message to send
         @sender Nickname of the sender
         @room Name of the room to send the message to
         @back BOOLEAN Should we send the message back to the sender to ? usefull for debug but use more bandwidth

         Does this room exist ?"""

        if self.allRooms.has_key(room):
            # We call the room
            self.allRooms[room].roomSendToAllClients(msg=data, nickName=sender, back=back)
        else:
            self.allNickNames[sender].clientSendErrorMessage(msg="No room by that name")


        def serverGetRoom(self, room):
            """
                Method to get informations about a particular room

                @room : Room to get information about
            """

            if self.allRooms.has_key(room):
                return self.allRooms[room].roomGetInfo()
            else:
                return "<error>No room by that name</error>"

    def checkPassword(self, nickName, password, sesId, ip):
        rc = True
        try:
            c = self.db.cursor()
            c.execute("select id from users where name = '%s' and upassword = '%s'" %\
                (escape_string(nickName), escape_string(password)))
            rs = c.fetchone()
            if rs is None:
                rc = False
                ids = -1
            else:
                ids = rs[0]
                s = "insert into sessions (sesid, userid, ip) values ('%s', %d, '%s')" %\
                    (sesId, ids, ip)
                print "Executing: ", s
                c.execute(s)

                s = "insert into connect_history (sesid, userid, lastip) values ('%s', %d, '%s')" %\
                    (sesId, ids, ip)
                print "Executing: ", s
                c.execute(s)

                self.db.commit();
        except:
            raise
        return (rc, ids)

    def isBlocked(self, uid):
        rc = True
        try:
            c = self.db.cursor()
            c.execute("select isblocked from users where id = %d" % uid)
            rs = c.fetchone()
            if rs is None:
                raise Exception(ERRORS[47] % uid)
            else:
                try:
                    if int(rs[0]) == 0:
                        rc = False
                    elif int(rs[0]) == 1:
                        rc = True
                    else:
                        raise Exception(ERRORS[45])
                    
                except Exception, msg:
                    logging.error("Wrong value for isblocked = '%s'" % str(rs[0]))
                    raise Exception(msg)
        except:
            raise
        return rc
  
    def isNickOk(self, nickName, password):
        """ Before accepting a nickname checking if it acceptable (non empty and non existant)
         @nickName Nickname requested

        return boolean
        """

        if nickName == "":
            return (False, 'Nickname is empty')
        if self.allNickNames.has_key(nickName):
            return (False, 'Nickname already taken')

        # Password check moved to isAuthorized()
        #if not self.checkPassword(nickName, password):
        #    return (False, "Bad password for user '%s'" % nickName)

        return True

    def serverAddClientToRoom(self, client, room='', parentR=''):
        """A client is trying to join a rooms

        This room may not exist, if so, we create it

        @client : Nickname of the client
        @room : Name of the room to join(create)
        @parentR : If we want to create a "Sub"Room, name of the ParentRoom (must exist)

        <Returns the instance of the Room
        """


        # La room existe déjà ?
        if self.allRooms.has_key(room):
            # On demande à la room de rajouter ce client
            self.allRooms[room].roomAddClient(client=client)
        else:
            # On demande à la room de se créer avec comme opérateur ce client
            self.allRooms[room] = \
                PalabreRoom(
                    rid = 0,
                    name = room, 
                    title = '', 
                    client = client, 
                    server = self, 
                    creatorId = 0, 
                    operatorId = 0, 
                    allowedUsersGroup = None, 
                    languageId = 0, 
                    temporary = 0, 
                    passwordProtected = 0, 
                    moderationAllowed = 0,
                    roomManagementLevel = 0, 
                    userManagementlevel = 0,
                    numberOfUsers = 0, 
                    numberOfSpectators = 0,
                    parentR = parentR)

        # On retourne l'instance room au client
        return self.allRooms[room]

    def serverAddClient(self,client):
        """When a client connects
        After identification (nickname) we add this client to self.allNickNames[]
        @client ; client Instance

        """

        self.allNickNames[client.nickName] = client

    def serverSendRoomsToClient(self, sesId = None):
        """A client ask for the list of all rooms (<getrooms />)

        We send him the list in XML :
            <rooms nb="NUMBER_OF_ROOMS">
                <room name="NAME">
                    <param name="PARAM">VALUE</param>
                </room>
            </rooms>

        For room name and params we call the Room Instance.roomShowParams();

        @client : Client Instance
        """
        try:
            c = self.db.cursor()
            c.execute("select ")

        except Exception, exc:
            raise
 
    def serverSendRoomsToClient_OLD(self, client):
        """A client ask for the list of all rooms (<getrooms />)

        We send him the list in XML :
            <rooms nb="NUMBER_OF_ROOMS">
                <room name="NAME">
                    <param name="PARAM">VALUE</param>
                </room>
            </rooms>

        For room name and params we call the Room Instance.roomShowParams();

        @client : Client Instance
        """

        listeR = "<rooms nb='%i'>" % len(self.allRooms)
        for p in self.allRooms.values():
            listeR += "\n" + p.roomShowParams()
        listeR += "\n</rooms>"
        client.clientSendMessage(msg=listeR)

    def serverRemoveRoom(self, room):
        """When a room is empty it is automaticaly destroyed

        @room : Room name
        """

        if self.allRooms.has_key(room):
            del self.allRooms[room]

    def isRootPass(self, password):
        """Checking Root Password

        @password : password to check

        <Returns Boolean"""

        # On pourrait tout aussi bien le stocker dans la base de donnée
        if password == self.rootPassword and self.rootPassword != '':
            return True
        else:
            return False

    def isAuthorized(self, nickName, password, sesId, ip):
        """  Method for authentification
        """
        return self.checkPassword(nickName, password, sesId, ip)

    def leaveAllRooms(self, uid):
        print 'leaving all rooms'

        if uid is None:
            print 'uis is None, return'
            return

        c = None

        try:
            c = self.db.cursor()

            s = "select name from users where id = %d" % uid
            c.execute(s)
            rs = c.fetchone()
            if rs is None or len(rs) == 0:
                raise Exception(ERRORS[15] % uid)
            name = string.strip(rs[0])

            s = "select rooms_id from users_rooms where users_id = %d" % uid
            print s
            c.execute(s)

            client_in_room = False
            rs = c.fetchall()
            for r in rs:
                print 'Client #%d now in room #%d, leaving...' % (uid, int(r[0]))
                client_in_room = True
                self.handleClientInRoom(uid = uid, rid = r[0], flag = EV_LEAVE, name = name)

            self.db.commit()
            self.db.begin()
            self.db.execute_immediate("delete from users_rooms where users_id = %d" % (uid))
            self.db.commit()
 
            out = "<leaveallroom error='0' uid='%d' />" % (uid)
 
            print out
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<leaveallroom error='1' msg=%s />" 
            print out % (str(exc))

    def handlePersonalMessage(self, from_uid, to_uid = None, rid = None, msgtype = None, text = None, from_name = None):
        print 'handlePersonalMessage'
        attrs = {}
        attrs["from_uid"] = from_uid
        attrs["type"] = msgtype
        attrs["text"] = text
        attrs["from_name"] = from_name

        if rid is not None:
            attrs["rid"] = rid

        if msgtype in [mtypes.M_PERSONAL, mtypes.M_PRIVATE] and to_uid is not None:
            attrs["to_uid"] = to_uid

            if rid is None:
                raise Exception(ERRORS[22])

            found = False
            for ids in self._map:
                if not isinstance(self._map[ids], PalabreClient):
                    continue

                if self._map[ids].ids == to_uid:
                    self._map[ids].sendCustomMessage(attrs)
                    found = True
                    break

            if not found:
                raise Exception(ERRORS[40] % to_uid)
        elif rid is not None:
            attrs["rid"] = rid

            c = self.db.cursor()
            s = "select users.id, users.name from users where users.id in (select users_id from users_rooms where rooms_id = %d)" % rid
            c.execute(s)

            rs = c.fetchall()

            for r in rs:
                ids = r[0]
                print 'ROOMS:> ', r, ids

                for ii in self._map:
                    if not isinstance(self._map[ii], PalabreClient):
                        continue

                    if self._map[ii].ids == ids:
                        self._map[ii].sendCustomMessage(attrs)
                        found = True
        elif msgtype == mtypes.M_BROADCAST:
            if attrs.has_key("id"):
                del attrs["id"]
            if attrs.has_key("rid"):
                del attrs["rid"]

            for ii in self._map:
                if not isinstance(self._map[ii], PalabreClient):
                    continue

                self._map[ii].sendCustomMessage(attrs)
        else:
            self._clients.sendCustomMessage(attrs)

    def silentUser(self, uid, period):
        found = False
        for ii in self._map:
            if not isinstance(self._map[ii], PalabreClient):
                continue

            if self._map[ii].ids == uid:
                found = True
                self._map[ii].silent = 1
                self._map[ii].silentPeriod = period
                self._map[ii].silentStart = time.time()

        if not found:
            raise Exception(ERRORS[40] % uid)

    def blockClient(self, uid, msg = "<error msg='You are blocked. Disconnect requested.' />"):
        ''' Disconnect blocked user '''

        for ii in self._map:
            if not isinstance(self._map[ii], PalabreClient):
                continue

            if self._map[ii].ids == uid:
                self._map[ii].clientSendMessage(msg)
                self._map[ii].handle_close()

    def setLastIP(self, uid):
        if uid is None:
            print 'uis is None, return'
            return

        c = None

        try:
            c = self.db.cursor()

            self.db.commit()
            self.db.begin()

            s = "select ip from sessions where userid = %d" % uid
            c.execute(s)
            rs = c.fetchall()
            print rs

            if len(rs) > 1:
                print "BAD:", rs
            addr = string.strip(rs[0][0])

            s = "update users set lastip = '%s' where id = %d" % (addr, uid)
            print s
            self.db.execute_immediate(s)
            self.db.commit()

            out = "<updatelastip error='0' uid='%d' />" % (uid)

            print out
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            out = "<updatelastip error='1' msg=%s />" 
            print out % (str(exc))

    def inviteUser(self, uid, rid):
        found = False

        for ids in self._map:
            if not isinstance(self._map[ids], PalabreClient):
                continue

            if self._map[ids].ids == uid:
                msg = "<inviteuser rid='%d' uid='%d' />" % (rid, uid)
                self._map[ids].clientSendMessage(msg)
                found = True
                break

        if not found:
            raise Exception(ERRORS[40] % uid)

    def notifyStop(self, reason = "unknown"):
        for ids in self._map:
            if not isinstance(self._map[ids], PalabreClient):
                continue

            self._map[ids].clientSendMessage("<server action='stop' reason='%s' />" % reason)

    def handleClientInRoom(self, uid, rid, flag, name):

        if flag == EV_LEAVE:
            msg = "<userleave id='%d' name='%s' rid='%d' />" % (uid, escape_string(name), rid)
        else:
            msg = "<userjoin id='%d' name='%s' rid='%d' />" % (uid, escape_string(name), rid)

        c = self.db.cursor()
        s = "select users_id from users_rooms where rooms_id = %d" % rid
        c.execute(s)
        rs = c.fetchall()

        if rs is None or len(rs) == 0:
            # there is no one in the room, we don't need to notify anybody
            return

        notifyList = []
        for r in rs:
            notifyList.append(r[0])
        print 'notifyList', notifyList

        for ids in self._map:
            if not isinstance(self._map[ids], PalabreClient):
                continue
            #print "ids=%d, uid=%d" % (self._map[ids].ids, uid)
            #print "notifyList: ", notifyList

            targetIds = self._map[ids].ids

            if targetIds != uid and targetIds in notifyList:
                # We don't need to notify ourselves
                print 'GOING:', ids
                self._map[ids].clientSendMessage(msg)

    def getConnectedUsers(self):
        out = []
        for ids in self._map:
            if not isinstance(self._map[ids], PalabreClient):
                continue

            out.append(self._map[ids].ids)
        return out
        

def _test():
    p = PalabreServer()

if __name__ == '__main__':
    _test()

# ---
