
#
# $Id: weather.py,v 1.9 2006/08/27 13:33:45 lightdruid Exp $
#

import sys
sys.path.insert(0, '../..')
from Plugin import Plugin, PluginException
from message import *
from icq import log

_loaded = True

try:
    import pymetar
except ImportError, exc:
    raise PluginException("Unable to initialize 'weather' plugin: " + str(exc))
    _loaded = False


class Weather(Plugin):
    _trusted_uin = []

    _category = "service"

    def isLoaded(self):
        return _loaded

    def onIncomingMessage(self, buddy, message):

        if buddy.uin in self._trusted_uin:
            log().log("WEATHER: '%s' is in trusted UINs" % buddy.uin)

            txt = message.getContents().lower().strip()
            if txt == 'weather':
                m = messageFactory("icq", buddy.name, buddy.uin, self.formatReport(), Outgoing)
                self.sendMessage(buddy, m)

                # Set 'blocked' flag - do not deisplay message
                message.blocked(True)
        else:
            log().log("WEATHER: '%s' is NOT in trusted UINs" % buddy.uin)

        return message

    def sendMessage(self, buddy = None, message = None):
        self._connector.sendMessage(message)

    # ---
    def __init__(self, station, connector):
        Plugin.__init__(self)

        self._station = station
        self._connector = connector['icq']

        self.report = None

    def setup(self, station = 'UMMS'):
        self._station = station

    def fetch(self):
        self.rf = pymetar.ReportFetcher(self._station)
        self.rawReport = self.rf.FetchReport()

        self.reportParser = pymetar.ReportParser()
        self.report = self.reportParser.ParseReport(self.rawReport)

    def formatReport(self):

        try:
            if self.report is None:
                self.fetch()
        except pymetar.NetworkException, exc:
            return "Report unavailable (%s)" % str(exc)

        s = ''
        s += "Weather report for %s (%s) as of %s" %\
            (self.report.getStationName(), self._station, self.report.getISOTime())
        s += "\n"
        s += "Values of \"None\" indicate that the value is missing from the report."
        s += "\n"
        s += "Temperature: %s C / %s F" %\
            (self.report.getTemperatureCelsius(), self.report.getTemperatureFahrenheit())
        s += "\n"
        s += "Relative Humidity: %s%%" % (self.report.getHumidity())
        s += "\n"
        if self.report.getWindSpeed() is not None:
            s += "Wind speed: %0.2f m/s" % (self.report.getWindSpeed())
        else:
            s += "Wind speed: None"
        s += "\n"
            
        s += "Wind direction: %s deg (%s)" %\
            (self.report.getWindDirection(), self.report.getWindCompass())
        s += "\n"
        if self.report.getPressure() is not None:
            s += "Pressure: %s hPa" % (int(self.report.getPressure()))
        else:
            s += "Pressure: None"
        s += "\n"

        s += "Weather: " + str(self.report.getWeather())
        s += "\n"
        s += "Sky Conditions: " + str(self.report.getSkyConditions())
        s += "\n"

        return s

    def reset(self):
        self.report = None


def _test():
    w = Weather('UMMS', None)
    print w.formatReport()

if __name__ == '__main__':
    _test()

# ---
