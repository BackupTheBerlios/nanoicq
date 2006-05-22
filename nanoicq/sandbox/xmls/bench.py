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
        #self.sock.send('<connect nickname="test_1" ></connect>')
        self.sock.xsend('<connect nickname="test_' + str(self.ids) + '" ></connect>')
        print 'connect request has been sent'

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

                if self.parseData(data):
                    self.genAction()
                data = ''
        self.sock.close()

    def genAction(self):
        next_one = randrange(4)

        print "From test_%d" % self.ids
        if next_one == 0:
            print 'sending <getrooms />'
            self.sock.xsend('<getrooms />')
        elif next_one == 1:
            print "sending <join room='XXX' />"
            self.sock.xsend('<join room="XXX" />')
        elif next_one == 2:
            z = randrange(MX)
            print "sending <join room='room_%d' />" % z
            self.sock.xsend('<join room="room_%d" />' % z)
        elif next_one == 3:
            z = randrange(MX)
            print "sending <join room='room_%d' />" % z
            self.sock.xsend('<join room="room_%d" />' % z)
        else:
            raise Exception('wrong seed')
  
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

                for a in node.attributes.items():
                    #attrs[p[0]] = p[1].encode("utf-8")
                    print a

                if node.nodeName == 'connect':
                    self.ping()
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

        self.max_clients = self.config.getint("bench", "clients")

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

        print "Waiting for 3 sec"
        time.sleep(3)
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
