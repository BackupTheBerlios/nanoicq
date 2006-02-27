
#
# $Id: Plugin.py,v 1.2 2006/02/27 14:55:17 lightdruid Exp $
#

import os
import sys
import glob
import traceback

from message import *
from buddy import Buddy

class Plugin:
    def __init__(self):
        pass

    def onIncomingMessage(self, buddy = None, message = None):
        raise NotImplementedError('onIncomingMessage')

def __my_path():
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname(os.path.abspath(root))
    except:
        return os.path.dirname(sys.argv[0])


def __load_plugins(plugin_dir):
    plugins = {}
    print os.path.join(plugin_dir, '*')
    for d in glob.glob(os.path.join(plugin_dir, '*')):
        dd = os.path.abspath(d)
        head, module = os.path.split(dd)

        # FIXME: temporary hack
        if module == 'CVS': continue

        print dd

        try:
            b = __import__(module).init_plugin()
        except (ImportError, AttributeError):
            print "Error loading plugin '%s'" % module
            traceback.print_exc()
        else:
            if module is None:
                print "Plugin '%s' is empty, not loaded" % module
            else:
                print "Loaded '%s' plugin" % module
                plugins[module] = (b)
    return plugins

def load_plugins(top = None, mp = None):
    if top is None:
        top = 'plugins'
    if mp is None:
        m_path = __my_path()
    else:
        m_path = mp
    sys.path = [os.path.join(m_path, top)] + sys.path
    return __load_plugins(top)

def _test():
    p = load_plugins()
    print p

    m = messageFactory("icq", 'user', '12345', 'text', Outgoing)
    b = Buddy()

    for k in p:
        p[k].onIncomingMessage(buddy = b, message = m)
    
if __name__ == '__main__':
    _test()

# ---
