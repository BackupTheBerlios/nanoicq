
#
# $Id: config.py,v 1.5 2006/02/27 10:29:29 lightdruid Exp $
#

import os

from ConfigParser import SafeConfigParser

class Config(SafeConfigParser):
    SUPPORTED_PROXIES = ['socks5', 'http']
    _DEFAULT_CONFIG = 'default.rc'

    def __init__(defaults = None):
        SafeConfigParser.__init__(defaults)

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
            dest_dir = "~"
        f1 = open(os.path.join(os.getcwd(), self._DEFAULT_CONFIG), 'rb')
        f2 = open(full_fn, 'wb')
        f2.write(f1.read())
        f1.close(); f2.close()


def _test():
    c = Config()
    c.read('sample.config')
    print c.get('icq', 'uin')
    print c.validate()
    c.checkFile("nanoicqrc")

if __name__ == '__main__':
    _test()

# ---
