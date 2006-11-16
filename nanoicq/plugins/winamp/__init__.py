
#
# $Id: __init__.py,v 1.2 2006/11/16 14:57:40 lightdruid Exp $
#

from winamp_plugin import Winamp, BOOTED

def init_plugin(connector):
    return (Winamp(connector), BOOTED)

# ---
