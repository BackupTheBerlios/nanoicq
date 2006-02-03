
#
# $Id: config.py,v 1.4 2006/02/03 10:41:36 lightdruid Exp $
#

from ConfigParser import SafeConfigParser

class Config(SafeConfigParser):
    SUPPORTED_PROXIES = ['socks5']

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


def _test():
    c = Config()
    c.read('sample.config')
    print c.get('icq', 'uin')
    print c.validate()

if __name__ == '__main__':
    _test()

# ---
