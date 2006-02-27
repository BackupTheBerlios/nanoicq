
#
# $Id: __init__.py,v 1.1 2006/02/27 13:55:46 lightdruid Exp $
#

def init_plugin():
    from weather import Weather
    return Weather()

# ---
