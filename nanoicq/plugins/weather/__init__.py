
#
# $Id: __init__.py,v 1.2 2006/03/09 15:36:01 lightdruid Exp $
#

def init_plugin(connector):
    from weather import Weather
    return Weather(station = 'UMMS', connector = connector)

# ---
