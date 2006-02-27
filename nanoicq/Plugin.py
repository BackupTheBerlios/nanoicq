
#
# $Id: Plugin.py,v 1.1 2006/02/27 13:55:46 lightdruid Exp $
#

import os
import sys
import glob
import traceback

from message import *

class Plugin:
    def onInconmingMessage(self, msg):
        raise NotImplementedError('onInconmingMessage')

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

    for d in glob.glob(os.path.join(plugin_dir, '*')):
        dd = os.path.abspath(d)
        head, module = os.path.split(dd)
        try:
            b = __import__(module).init_plugin()
        except (ImportError, AttributeError):
            print "Error loading plugin '%s'" % module
            traceback.print_exc()
        else:
            print "Loaded '%s' plugin" % module
            plugins[module] = (b)
    return plugins

def load_plugins():
    m_path = __my_path()
    sys.path = [os.path.join(m_path, 'plugins')] + sys.path
    return __load_plugins('./plugins')

def _test():
    p = load_plugins()
    print p
    
if __name__ == '__main__':
    _test()

# ---
