#!/usr/bin/python
# -*- coding: utf-8 -*-

# Palabre - palabreServer.py
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
import asyncore
import string
import signal
import sys
import os
import sys
import MySQLdb as DB
from datetime import datetime
from palabre import logging, version
from palabreClient import PalabreClient
from palabreRoom import PalabreRoom



class PalabreServer(asyncore.dispatcher):
    """PalabreServer Class - Main Class

     This class open the port and listen for connections
     It is the first to be initialized and instanciates
     the rooms and clients upon requests.
    """

    # Class to instanciate upon connection
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

    def checkDbStatus(self, db):
        checkTables = ['user']

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
            db = DB.connect(
                host = "10.3.13.7",
                port = 3306,
                user = "postnuke", 
                passwd = "postnuke", 
                db = "test")

            self.checkDbStatus(db)

            logging.debug("Connected")
        except DB.DatabaseError, exc:
            logging.error("DB connection: " + str(exc))

        return db

    def handle_accept(self):
        """Handle incoming connections
        Defines class variable channel_class
        """
        conn, addr = self.accept()
        self.channel_class(self, conn, addr, self.connectToDb())

    def handle_close(self):
        """When shuting down the server
        Closes log file
        Shutdown the server
        """
        self.logFile.close()
        self.serverShutDown()




    def writable(self):
        """
            ...
        """
        return 0




    def serverShutDown(self):
        """When asked to shutdown the server by root
        """

        logging.warning("Server shutdown requested")

        """ On envoit un message à tous les clients """

        for p in self.allNickNames.values():
            p.clientSendErrorMessage(msg="### Server is now going down ... ###")
            p.close()

        self.close()
        # !!!!DIRTY HACK ALERT!!!!
        # we have to find another way to do this
        # os._exit is indeed a very dirty hack and should not be used at all.
        # indeed i suck and don't understand much of what i do
        # the previous comment and its poor english was graciously 
        # brougth to you by lekma
        # indeed (i am so f***ing tired and it's only 20:13)
        #os._exit(0)


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


    def serverClientQuit(self, nickName):
        """Method to handle a client deconnection

        @nickName : Nickname of the client to disconnect.

        <Returns nothing"""
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


    def isNickOk(self, nickName):
        """ Before accepting a nickname checking if it acceptable (non empty and non existant)
         @nickName Nickname requested

        return boolean
        """
        # Si il est pas vide et pas déjà prit
        if nickName != "" and not self.allNickNames.has_key(nickName):
            return True
        else:
            return False




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






    def serverSendRoomsToClient(self, client):
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



    def isAuthorized(self, nickName, attrs):
        """TODO !!!  Method for authentification
        Example for MYSQL :
            Méthode à modifier pour paramétrer l'authentification

            if attrs.has_key('code') and attrs.has_key('password'):
                c = self.db.cursor()
                res = c.execute("SELECT * FROM t_connexions WHERE connexion_code LIKE '"+nickName+"'")

                c.execute("DELETE FROM t_connexions WHERE connexion_code LIKE '"+nickName+"'")
        """
        return True

def _test():
    p = PalabreServer()

if __name__ == '__main__':
    _test()

# ---
