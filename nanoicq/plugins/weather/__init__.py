
#
# $Id: __init__.py,v 1.3 2006/11/16 14:57:40 lightdruid Exp $
#

def init_plugin(connector):
    from weather import Weather, BOOTED
    return (Weather(station = 'UMMS', connector = connector), BOOTED)

# ---
