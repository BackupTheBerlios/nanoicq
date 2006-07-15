# -*- coding: utf-8 -*-

import sys, os, signal, time, threading, traceback, asyncore
from signal import SIGTERM, SIGINT

from palabre import config, logfile, logging, version, palabreServer

topServer = None

class palabreMain(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)
        self.setDaemon(True)


        # some default
        self.ip = ""
        self.port = 2468
        self.password = ""

        # read config
        if config.has_option("daemon", "ip") and config.get("daemon", "ip"):
            self.ip = config.get("daemon", "ip")
        if config.has_option("daemon", "port") and config.get("daemon", "port"):
            self.port = config.getint("daemon", "port")
        if config.has_option("admin", "password") and \
            config.get("admin", "password"):
            self.password = config.get("admin", "password")

        # These are used to catch startup errors of the asyncore server
        self.startError = None
        self.startedEvent = threading.Event()

    def start(self):

        threading.Thread.start(self)
        # as the asyncore.loop doesn't return, we wait 1 sec. to catch errors
        # before the server is declared as started
        self.startedEvent.wait(1.0)
        if self.startError:
            raise self.startError

    def run(self):

        try:
            global topServer
            self.server = palabreServer.PalabreServer(self.ip, self.port, \
                                                 self.password)
            topServer = self.server

            asyncore.loop()
        except Exception, e:
            logging.exception(str(e))
            self.startError = e
            return


class palabreLogFile:
    """File object class to redirect stdout and stderr."""
    def __init__(self, level):
        """Implement logging levels.
        @level : int -- can be any of:
            CRITICAL    50
            ERROR       40
            WARNING     30
            INFO        20
            DEBUG       10
            NOTSET      0
        """
        self.level = level

    def write(self, msg):
        """Implement the needed write method."""
        logging.log(self.level, msg)


class palabreDaemon:

    def __init__(self):

        self.pidfile = config.get("daemon", "pidfile")
        self.daemon = config.getboolean("daemon", "startdaemon")
                
        if not self.daemon:
            signal.signal(SIGINT, self.sig_handler)

        signal.signal(signal.SIGTERM, self.sig_term_handler)

    def sig_term_handler(self, signo, frame):
        #topServer.notifyStop()
        #time.sleep(1)
        pass

    def control(self, action):

        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if action == 'stop':
            self.stop(pid, False, 'Restarting server')
        elif action == 'start':
            self.start()
        elif action == 'restart':
            self.stop(pid, True, 'Restarting server')
            self.start()
        elif action == 'status':
            self.status(pid)

    def start(self, msg = None):

        logging.info("Starting Palabre...")

        if not __debug__ and os.path.exists(self.pidfile):

            if self.daemon:
                sys.stderr.write("Could not start, Palabre is already running (pid file '%s' exists).\n" % self.pidfile)
            logging.warning("Could not start, Palabre is already running (pid file '%s' exists)." % self.pidfile)
            logging.shutdown()
            logfile.close()
            sys.exit(1)
        else:
            if self.daemon:
                # Do first fork.
                try: 
                    pid = os.fork () 
                    if pid > 0:
                        # Exit first parent.
                        sys.exit (0)
                except OSError, e: 
                    sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
                    sys.exit(1)
                    
                # Decouple from parent environment.
                os.chdir("/") 
                os.umask(0) 
                os.setsid() 
                
                # Do second fork.
                try: 
                    pid = os.fork() 
                    if pid > 0:
                        # Exit second parent.
                        sys.exit(0)
                except OSError, e: 
                    sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
                    sys.exit(1)
    
            # close stdin
            sys.stdin.close()
            # redirect stdout and stderr to logging
            # in case we're not a daemon logging redirects
            # everything to sys.stderr anyway
            sys.stdout = palabreLogFile(20)  # level INFO
            sys.stderr = palabreLogFile(40)  # level ERROR
            # our process id
            pid = int(os.getpid())

            # main call
            try:
                # we send the main server in another thread (i forgot why)
                self.server = palabreMain()
                self.server.start()
                # if we get this far, we're started, write pidfile, log...
                file(self.pidfile,'w+').write("%s" % pid)
                logging.info("...started with pid: %s." % pid)
                # ...and sleep.
                while True:
                    time.sleep(1)
                #server.join()
            except Exception, e:
                sys.stdin = sys.__stdin__
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                traceback.print_exc()
                sys.exit(1)

    def stop(self, pid, restart, msg = None):

        logging.info("Stopping Palabre...")
        if not pid:
            if self.daemon:
                sys.stderr.write("Could not stop, Palabre is not running (pid file '%s' is missing).\n" % self.pidfile)
            logging.warning("Could not stop, Palabre is not running (pid file '%s' is missing)." % self.pidfile)
            if not restart:
                logging.shutdown()
                logfile.close()
                sys.exit(1)
        else:
            ## There should be a better way, but i'm too lazy to search... but
            ## i'm sure there's a better way
            
            # if we're not a daemon we should clean up before committing suicide
            if not self.daemon:
                os.remove(self.pidfile)
                logging.shutdown()
                logfile.close()
            try:
                self.server.server.notifyStop()
                time.sleep(1)

                while True:
                    os.kill(pid,SIGTERM)
                    time.sleep(1)
            except OSError, e:
                if e.strerror.find("No such process") >= 0:
                    os.remove(self.pidfile)
                    if not restart:
                        logging.info("...stopped.")
                        logging.shutdown()
                        logfile.close()
                        sys.exit(0)
                else:
                    logging.error("%s" % e.strerror)
                    logging.shutdown()
                    logfile.close()
                    sys.exit(1)

    def status(self, pid):

        sys.stdout.write("Palabre %s\n" % version)
        if not pid:
            sys.stdout.write("Palabre is not running.\n")
        else:
            sys.stdout.write("Palabre is running, pid: %s.\n" % pid)

    def sig_handler(self, signo, frame):
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except Exception, e:
            raise
        self.stop(pid, False)
