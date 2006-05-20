#!/usr/bin/python

# $Id: Message.py,v 1.1 2006/05/20 21:47:54 lightdruid Exp $

import time
from util import *

_mtypes = [
M_PERSONAL,
M_PRIVATE, # FIXME what's the difference from M_PERSONAL
M_PUBLIC,
M_BROADCAST,
M_GET_RECORDS_LIST,
M_GET_RECORD,
M_CUSTOM,
M_STORE_RECORD
] = range(8);

 
class Message:

    def __init__(self):
        self.time = time.localtime()
        self.text = None
        self.type = M_CUSTOM

        assert self.type in _mtypes

    def send(self, sessId, message):
        fail()

    def onData(self, message):
        fail()


if __name__ == '__main__':
    m = Message()

#---

