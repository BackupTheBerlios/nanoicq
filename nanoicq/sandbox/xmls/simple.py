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

 
    def parseData(self, data):
        #data = string.replace(data, "\0", "")
        #try:
        #    print '21:', data[21:], ord(data[21])
        #except:
        #    pass

        data = string.split(data, "\0")
        #print dt

        for dt in data:
            print "[%s]" % dt

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
                    #self.sock.xsend("<creategroup name='abcd' moderationLevel='1' />")
                    #self.sock.xsend("<getgroupproperties id='45' />")
                    #self.sock.xsend("<setgroupproperties id='13' name='first one' />")
                    #self.sock.xsend("<listmembers id='0' />")
                    #self.sock.xsend("<getuserproperties id='1' />")
                    #self.sock.xsend("<getuserproperties id='2' />")
                    #self.sock.xsend("<getuserproperties id='3' />")
                    #self.sock.xsend("<setuserproperties id='3' languageid='10' />")
                    #self.sock.xsend("<getroomlist />")
                    self.sock.xsend("<getroomproperties id='1' />")
          
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

        SEC = 10
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
