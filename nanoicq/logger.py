
from SingletonMixin import *
from utils import *

class LogException(Exception):
    pass


DEBUG = 0
INFO = 1
ERROR = 2

class _Log:
    _allowed_levels = [DEBUG, INFO, ERROR]

    def __init__(self, level = 0):
        self._level = level

    def log(self, a, b = None):
        if b is None:
            level = 0
            msg = a
        elif a in self._allowed_levels:
            level = a
            msg = b
        else:
            raise LogException("Wrong message type")

        if level >= self._level:
            print "LOG (%d):" % level, msg

    def setLevel(self, level):
        self._level = level

    def packetin(self, msg):
        self.log("<- " + ashex(msg))

    def packetout(self, msg, verbose = False):
        self.log("-> " + ashex(msg))
        if verbose:
            self.log("->\n" + coldump(msg))


class Log(_Log, Singleton): 
    def __init__(self):
        Singleton.__init__(self)
        _Log.__init__(self)


def log():
    return Log.getInstance()


if __name__ == '__main__':

    import unittest
    
    class Test1(unittest.TestCase):
        def test1(self):
            log1 = Log.getInstance()
            log2 = Log.getInstance()
            self.assertEquals(id(log1), id(log2))

        def test2(self):
            logs = []
            for i in range(10):
                logs.append(log())
            for i in range(10 - 1):
                logs[i].log(0, 'test' + str(i))
                self.assertEquals(id(logs[i]), id(logs[i+1]))

        def test3(self):
            log1 = log()
            log1.setLevel(2)
            log1.log('This line should not be in output')

    unittest.main()

# ---

