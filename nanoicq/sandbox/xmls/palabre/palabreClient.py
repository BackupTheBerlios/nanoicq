# -*- coding: utf-8 -*-

# Palabre - palabreClient.py
#
# Copyright 2003-2005 Célio Conort
#
# This file is part of Palabre.
#
# Palabre is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2, or (at your option) any later version.
#
# Palabre is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with program; see the file COPYING. If not,
# write to the Free Software Foundation, Inc., 59 Temple Place
# - Suite 330, Boston, MA 02111-1307, USA.

import socket
import asynchat
import xml.dom.minidom as xmldom
import xml.sax.saxutils as SAX
import string

from palabre import logging

import MySQLdb as DB


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

                        creatorid='%d',
                        operatorid='%d',

                        allowedUsers='%d',
                        languageid='%d',
                        temporary='%d',
                        passwordProtected='%d',

                        moderationAllowed='%d',
                        roomManagementLevel='%d',
                        userManagementlevel='%d',

                        numberOfUsers='%d',
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
        """Class Constructor

        @nickName   Nickname to identify the user.
        @server     PalabreServer Instance to which we are connected
        @conn       Connection instance
        @addr       Client IP Addr
        @carTerm    Flash sends 'null character' to end a request : \0
        @data       String to increment until "carTerm"
        @loggedIn   Has he supplied a correct nickName ?
        @isRoot     Is Client Root (supplied Root Password)

        @allMyRooms[ ]  Dictionnaries of all rooms this client has joined



        """
        """
            Constructeur du client
            Définition des variable, du 'terminator'
            etc ...
        """

        # Asynchat initialise son client
        # Asynchat initialisation ... (main class for sending and receiving messages */
        asynchat.async_chat.__init__ (self, conn)

        # Pour que le client retrouve le serveur
        self.server = server

        # Pour que le client retrouve sa connexion
        self.conn = conn

        # Database connection
        self.db = db

        # Adresse Ip ?
        self.addr = addr[0]

        # Quel caractère détermine la fin de l'envoi d'un message ?
        # Null character
        self.carTerm = "\0"

        # Inherited from asynchat ..
        self.set_terminator (self.carTerm) # Ici c'est un caractère null (Flash default)

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
        out = ["<groups>"]
        try:
            c = self.db.cursor()
            c.execute("select id, name, mlevel from groups order by name")
            rs = c.fetchall()
            for r in rs:
                print r
                out.append("<group id=%d name=%s moderationLevel=%d />" %\
                    (Q(r[0]), Q(r[1]), Q(r[2])))
        except:
            raise

        out.append("</groups>")
        self.clientSendMessage("\n".join(out))

    def createGroup(self, sesId = None, name = None, moderationLevel = None):
        print 'creating group...', name, moderationLevel

        out = "<creategroup isOk='0' msg=%s />"
        try:
            c = self.db.cursor()
            c.execute("insert into groups (name, mlevel) values ('%s', %d)" %\
                (DB.escape_string(name), int(moderationLevel)))
            c.execute("select id, name, mlevel from groups where name = '%s' and mlevel='%d'" %\
                (DB.escape_string(name), int(moderationLevel)))

            r = c.fetchone()

            out = ["<creategroup isOk='1'>"] 
            out.append("<group id='%d' name='%s' moderationLevel='%d' />" %\
                    (r[0], DB.escape_string(r[1]), r[2]))
            out.append("</creategroup>")
            self.clientSendMessage("\n".join(out))
        except Exception, exc:
            self.clientSendMessage( out % Q(str(exc)) )

    def getGroupProperties(self, sesId = None, gid = None):
        print 'retrieving group properties...', gid

        out = "<getgroupproperties isOk='0' msg=%s />"
        try:
            c = self.db.cursor()
            c.execute("select id, name, mlevel from groups where id='%d'" % int(gid))

            r = c.fetchone()
            if r is None:
                raise Exception("Can't find group with id='%d'" % int(gid))

            out = "<getgroupproperties isOk='1' id='%d' name='%s' moderationLevel='%d' />" %\
                (r[0], DB.escape_string(r[1]), r[2])
            self.clientSendMessage(out)
        except Exception, exc:
            self.clientSendMessage( out % Q(str(exc)) )

    def setGroupProperties(self, sesId = None, gid = None, name = None, moderationLevel = None):
        print 'retrieving group properties...', gid

        out = "<setgroupproperties isOk='0' msg=%s />"
        try:
            c = self.db.cursor()

            s = 'update groups set '
            if name is not None:
                s += " name = '%s' " % DB.escape_string(name)
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
                    (r[0], Q(r[1])) )

            out.append("</listmembers>");
 
            self.clientSendMessage("\n".join(out))
        except Exception, exc:
            raise
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
            for r in rs:
                out.append("<client id='%d' name=%s groupid='%d' languageid='%d' isblocked='%d' />" %\
                    (r[0], Q(r[1]), r[2], r[3], r[4])
                )

            out.append("</getuserproperties>");
 
            self.clientSendMessage("\n".join(out))
        except Exception, exc:
            raise
            out = "<getuserproperties isOk='0' msg=%s />" 
            self.clientSendMessage( out % Q(str(exc)) )

    def setUserProperties(self, sesId = None, attrs = {}):
        uid = int(attrs['id'])
        del attrs['id']

        print 'setting user properties... %d' % int(uid)

        c = None
        try:
            c = self.db.cursor()
            s = 'update users set '

            if attrs.has_key('name'):
                s += " name = %s " % DB.escape_string(attrs['name'])
            if attrs.has_key('languageid'):
                s += " languageid = '%d' " % int(attrs['languageid'])
            if attrs.has_key('password'):
                s += " password = %s " % DB.escape_string(attrs['password'])
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
                    (r[0], Q(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12])
                )

            out.append("</getroomlist>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            raise
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

            c.execute(s)

            out = ["<getroomproperties isOk='1' >"]

            rs = c.fetchall()
            for r in rs:
                out.append(_roomTemplate %\
                    (r[0], Q(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12])
                )

            out.append("</getroomproperties>");
 
            self.clientSendMessage("\n".join(out))
            safeClose(c) 
        except Exception, exc:
            safeClose(c)
            raise
            out = "<getroomproperties isOk='0' msg=%s />" 
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

            # Le client doit être logué pour faire la majorité des actions
            #
            # Client must be identified
            #
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

        # asynchat vire le client ... il est plus là
        asynchat.async_chat.close (self)

        # Pour débuguer
        logging.info("Connection lost for %s(%s)" % (self.nickName, self.addr))

        # Log off from DB
        try:
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
            self.clientSendErrorMessage(msg="No NickName Attribute")
            return

        nickName = attrs['nickname']
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
        if self.server.isAuthorized(nickName, password):

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

        # Pour info de débug ...
        # Debug information
        logging.info("Disconnection requested by %s(%s)" % (self.nickName, self.addr))

        # On informe l'instance serveur
        # Elle peut donc le supprimer des rooms et de sa liste
        # Notifying Server
        self.server.serverClientQuit(nickName=self.nickName)

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

