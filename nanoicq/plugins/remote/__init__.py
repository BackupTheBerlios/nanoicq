
#
# $Id: __init__.py,v 1.1 2006/08/21 22:19:21 lightdruid Exp $
#

def init_plugin(connector):
    from remote import Remote
    return Remote()

# ---
