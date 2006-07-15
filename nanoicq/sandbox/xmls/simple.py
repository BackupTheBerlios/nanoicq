#!/usr/bin/python

#from palabre import config

import sys, socket, time, select, string
import xml.dom.minidom as xmldom 
from threading import Thread
from ConfigParser import SafeConfigParser
from random import randrange, seed

GAP = 0.1
BUF_LEN = 1024 * 10
prefix = "<?xml version='1.0' encoding='utf-8' ?>"
MX = 10

class XMLSocket(socket.socket):
    def __init__(self, f, t):
        socket.socket.__init__(self, f, t)

    def xsend(self, data):
        self.send(data + "\0")


class Client(Thread):
    def __init__(self, ids, addr):
        Thread.__init__(self)
        self.ids = ids
        self.addr = addr
        self.running = 1

    def xml_connect(self):
        req = '<connect nickname="test_' + str(self.ids) + '" password="pass_' + str(self.ids) + '" ></connect>'
        req = '<connect nickname="ab" password="ab" ></connect>'
        print req
        self.sock.xsend(req)
 
    def run(self):
        seed(self.ids)
        self.sock = XMLSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr)

        self.xml_connect()
        data = ''

        while self.running:
            time.sleep(GAP)

            rd, wr, ex = select.select([self.sock.fileno()], [], [], 1)
            for fd in rd:
                #print 'we got data on handle', fd
                #print dir(self.sock)
                data += self.sock.recv(BUF_LEN)
                print 'data:', data

                if data[-1] != '\0' or len(data) == 0:
                    continue

                self.parseData(data)
                data = ''
        self.sock.close()

    def joinLeave(self):
        self.sock.xsend("<listusers id='3' />")
        self.sock.xsend("<joinroom id='3' />")
        self.sock.xsend("<listusers id='3' />")
        self.sock.xsend("<leaveroom id='3' />")
        self.sock.xsend("<listusers id='3' />")

 
    def parseData(self, data):
        #data = string.replace(data, "\0", "")
        #try:
        #    print '21:', data[21:], ord(data[21])
        #except:
        #    pass

        data = string.split(data, "\0")
        #print dt

        for dt in data:
            print "%s" % dt

            if len(dt) == 0:
                continue

            doc = None
            try:
                doc = xmldom.parseString(dt)
            except:
                f = open("test_%d.log" % self.ids, "wb")
                f.write(dt)
                f.close()
                raise

            for node in doc.childNodes:
                print 'node:', node.nodeName
                if node.nodeName == "connect":
                    #self.sock.xsend("<listgroups />")
                    #self.sock.xsend("<creategroup name='abcd0000000000000000000000000000000000000000abcd0000000000000000000000000000000000000000abcd0000000000000000000000000000000000000000abcd0000000000000000000000000000000000000000abcd0000000000000000000000000000000000000000abcd0000000000000000000000000000000000000000abcd0000000000000000000000000000000000000000abcd0000000000000000000000000000000000000000' moderationLevel='1' />")
                    #self.sock.xsend("<creategroup name='123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123123' moderationLevel='1' />")
                    #self.sock.xsend("<creategroup name='testgroup1' moderationLevel='1' />")
                    #self.sock.xsend("<getgroupproperties id='1' />")
                    #self.sock.xsend("<setgroupproperties id='2' name='andrey group123' moderationLevel='123'  />")
                    #self.sock.xsend("<listmembers id='550' />")
                    #self.sock.xsend("<getuserproperties id='4' />")
                    #self.sock.xsend("<getuserproperties id='234' />")
                    #self.sock.xsend("<getuserproperties id='3' />")
                    #self.sock.xsend("<setuserproperties id='4' moderationlevel='0' />")
                    #self.sock.xsend("<setuserproperties id='3' groupid='3' />")
                    #self.sock.xsend("<deletegroup id='22' />")
                    #self.sock.xsend("<setuserproperties id='8' isblocked='0' />")

                    #self.sock.xsend("<getroomproperties id='1' />")
                    #self.sock.xsend("<setroomproperties id='1' passwordProtected='1' publicPassword='abcde' />")
                    #self.sock.xsend("<getroomproperties id='1' />")

                    #self.sock.xsend("<createroom name='zzzzz' temporary='0' />")

                    s = '''
                    <createroom numberOfSpectators="0" numberOfUsers="0" userManagementlevel="0" roomManagementLevel="0" moderationAllowed="0" passwordProtected="0" temporary="0" languageid="0" allowedUsers="0" operatorid="0" creatorid="0" name="room #4" />

                    '''

                    s = '''
<setroomproperties numberOfSpectators="0" numberOfUsers="0" userManagementlevel="0" roomManagementLevel="0" moderationAllowed="0" passwordProtected="1" temporary="0" languageid="0" allowedUsers="0" operatorid="0" creatorid="2" publicPassword="asd" id="11" />
                    '''
                    #self.sock.xsend(s)
                    self.sock.xsend("<getroomlist />")
                    #self.sock.xsend("<createroom name='fl' > <client id='1' /> <client id='2' />  </createroom>")
                    #self.sock.xsend('<getroomproperties id="2" />')
                    #self.sock.xsend('<setroomproperties id="2" pvtPassword="newone" allowedGroupId="3" />')

                    #self.sock.xsend('<setroomsecurity pvtPassword="newone" newPvtPassword="123" pvtPasswordProtected="1" id="2" />')

                    #self.sock.xsend("<getroomlist />")
 
                    #self.sock.xsend('<deletealloweduser uid="3" rid="11" />')
                    #self.sock.xsend('<addalloweduser uid="2" rid="1" />')
                    #self.sock.xsend('<listalloweduser rid="1" />')

                    #self.sock.xsend('<joinroom id="11" password="asd" />')
                    #self.sock.xsend("<listusers id='11' />")
                    #self.sock.xsend('<addalloweduser uid="2" rid="2" />')
                    #self.sock.xsend('<redirectuser uid="2" from-rid="11" to-rid="2" />')

                    self.sock.xsend('<userlookup name="zz" />')


                    #self.sock.xsend("<getuserproperties id='4' />")
                    #self.sock.xsend('<setuserproperties isblocked="0" id="4" />')
                    #self.sock.xsend("<getuserproperties id='3' />")

                    #self.sock.xsend("<delroom id='2' />")

                    #self.sock.xsend("<joinroom id='1' password='abcde' />")
                    #self.sock.xsend("<joinasspectator rid='1' password='abcde' />")
                    #self.sock.xsend("<listusers id='1' />")
                    #self.sock.xsend("<leaveroom id='1' />")

                    #self.sock.xsend("<inviteuser uid='1' rid='1' />")

                    #self.sock.xsend("<joinroom id='2' password='abcde' />")
                    #self.sock.xsend("<leaveroom id='1' />")
                    #self.sock.xsend("<locateuser id='4' />")

                    #self.sock.xsend("<listblockedusers />")

                    #self.sock.xsend("<joinroom id='1' />")
                    #self.sock.xsend("<joinroom id='1' password='abcde' />")
                    #self.sock.xsend("<message text='hi' type='3' />")
                    #self.sock.xsend("<silentuser id='3' period='3' />")
                    #self.sock.xsend("<message text='hi' type='3' />")
                    #self.sock.xsend("<joinroom id='1' password='abc' />")

                    #self.sock.xsend("<leaveroom id='5' />")
                    #self.sock.xsend("<listusers id='1' />")
                    #self.sock.xsend("<listusers id='2' />")

                    #self.sock.xsend("<grouplookup name='group 2' />")
                    #self.joinLeave()
              
                for a in node.attributes.items():
                    #attrs[p[0]] = p[1].encode("utf-8")
                    print a

                if node.nodeName == 'connect':
                    #self.ping()
                    return False
        return True


    def ping(self):
        self.sock.xsend('<ping/>')
   
class Bench:
    def __init__(self):

        self.config = SafeConfigParser()
        self.config.readfp(open('./bench.conf', 'rb'))

        self.host = self.config.get("server", "address")
        self.port = self.config.getint("server", "port")

        self.max_clients = 1

    def createSocket(self):
        sock = XMLSocket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect( (self.host, self.port) )
        return sock

    def run(self):
        self.clients = []
        for ii in range(self.max_clients):
            self.clients.append(Client(ii, (self.host, self.port) ))

        print "Clients queue has been initialized"

        print "Starting %d clients..." % self.max_clients
        for c in self.clients:
            c.start()

        SEC = 4
        print "Waiting for %d sec" % SEC
        time.sleep(SEC)
        for c in self.clients:
            c.running = 0
         
        print "All clients are started"
        for c in self.clients:
            c.join()
  

def _test():
    b = Bench()
    b.run()


if __name__ == '__main__':
    _test()

# ---
