
#
# $Id: __init__.py,v 1.2 2006/11/16 14:57:40 lightdruid Exp $
#

def init_plugin(connector):
    from remote import Remote, BOOTED
    return (Remote(), BOOTED)

# ---
