# -*- coding: utf-8 -*-

# Palabre - __init__.py
#
# Copyright 2003-2005 Célio Conort
#
# This file is part of Palabre.
#
# Palabre is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2, or (at your option) any later version.
#
# Palabre is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with program; see the file COPYING. If not,
# write to the Free Software Foundation, Inc., 59 Temple Place
# - Suite 330, Boston, MA 02111-1307, USA.

import ConfigParser, logging, os

# version
version = "0.4"

if os.name == "posix":
    # config file setup
    config = ConfigParser.SafeConfigParser()
    config.readfp(open('/etc/palabre.conf'))
        
    # log setup
    levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    # the following is a workaround, cause contrary to what it claims
    # in the documentation, the logging module IS NOT threadsafe!!!
    # remember to close it after logging.shutdown()
    logfile = file(config.get("logging", "logfile"), 'a')
    # now we can configure the logging
    logging.basicConfig(level=levels[config.get("logging", "loglevel")],
                        format="%(asctime)s - [%(filename)-24s %(lineno)-4d]: %(process)-5d %(levelname)-8s %(message)s",
                        stream=logfile)

    if not config.getboolean("daemon", "startdaemon"):
        print "----------------------------------------------"
        print "Palabre not started as daemon !"
        print "Please edit  /etc/palabre.conf"
        print "----------------------------------------------"        
        # define a Handler which writes messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(levels[config.get("logging", "loglevel")])
        # set a format which is simpler for console use
        #formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
        #formatter = logging.Formatter("%(asctime)s - [%(filename)-24s %(lineno)-4d]: %(process)-5d %(levelname)-8s %(message)s")

        formatter = logging.Formatter("%(asctime)s [%(filename)s %(lineno)-4d]: %(levelname)-8s %(message)s")
 
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
