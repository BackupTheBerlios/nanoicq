
#
# $Id: __init__.py,v 1.1 2006/10/19 10:17:03 lightdruid Exp $
#

from winamp_plugin import Winamp

def init_plugin(connector):
    return Winamp(connector)

# ---
