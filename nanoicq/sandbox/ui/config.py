
#
# $Id: config.py,v 1.7 2006/08/15 11:29:47 lightdruid Exp $
#

import os

from ConfigParser import *

class Config(SafeConfigParser):
    SUPPORTED_PROXIES = ['socks5', 'http']
    _DEFAULT_CONFIG = 'default.rc'

    def __init__(defaults = None):
        SafeConfigParser.__init__(defaults)

    def safeGet(self, sect, name):
        try:
            return self.get(sect, name)
        except NoSectionError:
            return None

    def safeGetBool(self, sect, name):
        try:
            return self.getboolean(sect, name)
        except:
            return None

    def safeSet(self, sect, name, val):
        try:
            self.set(sect, name, val)
        except NoSectionError:
            self.add_section(sect)
            self.set(sect, name, val)

    def validate(self):
        ''' Some basic checks '''
        problems = []
        if self.has_option('icq', 'proxy.type'):
            if not self.has_option('icq', 'proxy.server'):
                problems.append("Proxy type set, but no proxy server specified")
            pt = self.get('icq', 'proxy.type')
            if pt not in self.SUPPORTED_PROXIES:
                problems.append("Unknown proxy type (%s), only %s supported" %\
                    (pt, ", ".join(self.SUPPORTED_PROXIES)))
        return problems

    def checkFile(self, fn):
        full_fn = os.path.join(os.getcwd(), fn)
        if os.path.exists(full_fn):
            return True
        print "Config file '%s' does not exits, creating default one" % fn
        if os.name == 'nt':
            dest_dir = os.getcwd()
        else:
            dest_dir = os.path.expandvars("$HOME") or os.getcwd()
        f1 = open(os.path.join(os.getcwd(), self._DEFAULT_CONFIG), 'rb')
        f2 = open(full_fn, 'wb')
        f2.write(f1.read())
        f1.close(); f2.close()

    def read(self, filenames):
        self.configFileName = filenames
        SafeConfigParser.read(self, filenames)

    def write(self):
        fp = open(self.configFileName, 'wb')
        SafeConfigParser.write(self, fp)
        fp.close()

def _test():
    c = Config()
    c.read('sample.config-1')
    print c.safeGet('icq', 'uin')
    print c.validate()
    c.checkFile("nanoicqrc")
    c.safeSet('icq', 'uin', '123')
    c.write()

if __name__ == '__main__':
    _test()

# ---
