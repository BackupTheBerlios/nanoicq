
#
# $Id: Plugin.py,v 1.4 2006/03/06 11:17:57 lightdruid Exp $
#

import os
import sys
import glob
import traceback

import wx

from message import *
from buddy import Buddy
from icq import log

class Plugin(wx.EvtHandler):
    def __init__(self):
        wx.EvtHandler.__init__(self)

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

    for d in glob.glob(os.path.join(plugin_dir, '*')):
        dd = os.path.abspath(d)
        head, module = os.path.split(dd)

        # FIXME: temporary hack
        if module == 'CVS': continue

        try:
            b = __import__(module).init_plugin()
        except (ImportError, AttributeError):
            log().log("Error loading plugin '%s'" % module)
            traceback.print_exc()
        else:
            if module is None:
                log().log("Plugin '%s' is empty, not loaded" % module)
            else:
                log().log("Loaded '%s' plugin" % module)
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
    log().log(p)

    m = messageFactory("icq", 'user', '12345', 'text', Outgoing)
    b = Buddy()

    for k in p:
        p[k].onIncomingMessage(buddy = b, message = m)
    
if __name__ == '__main__':
    _test()

# ---