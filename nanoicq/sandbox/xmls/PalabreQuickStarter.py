#!/usr/bin/python
# -*- coding:utf-8-*-
#
# This file is just to start palabre without installing it
# It is not safe, does not provide real log, ...
# So you can test but .. that's it.
#


from palabre.palabreServer import PalabreServer
import asyncore
import os
import time
import logging
import ConfigParser

##CONFIGURATION IN ./etc/palabre.conf

print "-------------------------------------------------------"
print "Palabre 0.4 Started in QuickStart Mode"
print "Only use this mode for testing purposes"
print "-------------------------------------------------------"

# log setup
levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

config = ConfigParser.SafeConfigParser()

config.readfp(open('./etc/palabre.conf'))

# config.get("logging", "logfile")
logfile = file('./palabre.log', 'a')

# now we can configure the logging
logging.basicConfig(level=levels[config.get("logging", "loglevel")],
                        format="%(asctime)s - [%(filename)-2s %(lineno)-4d]: %(levelname)-2s %(message)s",
                        stream=logfile)
# define a Handler which writes messages or higher to the sys.stderr
if not config.getboolean("daemon", "startdaemon"):
  console = logging.StreamHandler()
  console.setLevel(levels[config.get("logging", "loglevel")])
  # set a format which is simpler for console use
  #formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
  formatter = logging.Formatter("%(asctime)s - [%(filename)-2s %(lineno)-4d]: %(levelname)-2s %(message)s")
  # tell the handler to use this format
  console.setFormatter(formatter)
  # add the handler to the root logger
  logging.getLogger('').addHandler(console)

ip = config.get("daemon", "ip").strip()
port = int(config.get("daemon", "port"))
passw = config.get("admin", "password")

myServer = PalabreServer(ip,port,passw )

asyncore.loop()
