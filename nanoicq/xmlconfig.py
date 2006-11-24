
#
# $Id: xmlconfig.py,v 1.1 2006/11/24 10:28:37 lightdruid Exp $
#

from lxml import etree as E

import types

class XmlConfig:
    def __init__(self):
        self._p = E.XMLParser(remove_blank_text=True)
        self._x = None
        self._f = None

        # If False, then preserve original xml structure,
        # otherwise original xml will be reformatted, it
        # could be a little bit confusing
        self._pretty_print = False

    def setPrettyPrint(self, flag):
        self._pretty_print = flag

    def _openFile(self, x, mode=None):
        if mode is None:
            mode = "rb"
        if type(x) in types.StringTypes:
            f = open(x, mode)
        elif type(x) == types.FileType:
            f = x
        else:
            raise Exception("Unknown type of argument, must be string of file")
        return f

    def read(self, x):
        f = self._openFile(x)
        try:
            self._readFromFile(f)
        finally:
            f.close()

    def save(self, x):
        f = self._openFile(x, "wb")
        try:
            print >> f, E.tostring(self._x, pretty_print=self._pretty_print)
        finally:
            f.close()
        
    def set(self, path, value):
        self._x.xpath(path)[0].text = str(value)

    def get(self, path, default=None):
        rc = self._x.xpath(path)
        if len(rc) == 0:
            if default is not None:
                rc = default
            else:
                rc = None
        else:
            rc = rc[0].text
        return rc

    def getInt(self, path, default=None):
        rc = self.get(path, default)
        return long(rc)

    def getBool(self, path, default=None):
        rc = self.get(path, default)
        return bool(rc)

    def safeGetInt(self, path, default=None):
        rc = self.get(path, default)
        try:
            return long(rc)
        except TypeError, e:
            return None

    def _readFromFile(self, f):
        if self._pretty_print:
            self._x = E.parse(f, self._p)
        else:
            self._x = E.parse(f)

def _test():
    xc = XmlConfig()
    xc.read("options.xml")
    print xc.getInt("./Options/Network/ICQ/Port")
    xc.set("./Options/Network/ICQ/Port", 44)
    print xc.getInt("./Options/Network/ICQ/Port")
    xc.save('asd')

if __name__ == '__main__':
    _test()

# ---
