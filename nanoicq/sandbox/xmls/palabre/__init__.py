# -*- coding: utf-8 -*-

import ConfigParser, logging, os

# version
version = "0.4"

def escape_string(s):
    return s.replace("'", "''")


if os.name in ["posix", "nt"]:
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

        formatter = logging.Formatter("%(asctime)s : %(levelname)-8s %(message)s")
 
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
