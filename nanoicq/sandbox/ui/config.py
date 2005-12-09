
#
# $Id: config.py,v 1.1 2005/12/09 12:09:28 lightdruid Exp $
#


from ConfigParser import SafeConfigParser

class Config(SafeConfigParser):
    def __init__(defaults = None):
        SafeConfigParser.__init__(defaults)

def _test():
    c = Config()
    c.read('sample.config')
    print c.get('General', 'a')

if __name__ == '__main__':
    _test()

# ---
