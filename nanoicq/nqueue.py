
#
# $Id: nqueue.py,v 1.1 2006/11/23 16:25:57 lightdruid Exp $
#

from Queue import Queue
from SingletonMixin import *

import threading

class _NQueue(Queue):
    ''' Just a wrapper to ensure we have threading '''
    pass


class NQueue(_NQueue, Singleton): 
    def __init__(self, *kw, **kws):
        Singleton.__init__(self)
        _NQueue.__init__(self)


def nqueue():
    return NQueue.getInstance()


if __name__ == '__main__':
    n1 = nqueue()
    n2 = nqueue()
    print n1, n2

# ---
