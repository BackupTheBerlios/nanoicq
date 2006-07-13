#!/usr/bin/python

# $Id: Message.py,v 1.2 2006/07/13 11:27:16 lightdruid Exp $

import time
from util import *

class mtypes:
    M_PERSONAL          = 0
    M_PRIVATE           = 1
    M_PUBLIC            = 2
    M_BROADCAST         = 3
    M_GET_RECORDS_LIST  = 4
    M_GET_RECORD        = 5
    M_CUSTOM            = 6
    M_STORE_RECORD      = 7

 
class Message:

    def __init__(self):
        self.time = time.localtime()
        self.text = None
        self.type = M_CUSTOM

        #assert self.type in mtypes

    def send(self, sessId, message):
        fail()

    def onData(self, message):
        fail()


if __name__ == '__main__':
    m = Message()

#---

