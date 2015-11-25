#!/usr/bin/python

import os
import os.path
import sys
import logging
from logging import handlers
import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy.lib import auth_digest
import logging
import json
from threading import Thread

# Add some headers to ask browser for more secure page rendering
# https://cherrypy.readthedocs.org/en/3.3.0/progguide/security.html
def secureheaders():
    headers = cherrypy.response.headers
    headers['X-Frame-Options'] = 'DENY'
    headers['X-XSS-Protection'] = '1; mode=block'
    headers['Content-Security-Policy'] = "default-src='self'"
    if (cherrypy.server.ssl_certificate != None and cherrypy.server.ssl_private_key != None):
        headers['Strict-Transport-Security'] = 'max-age=31536000' # one year

cherrypy.tools.secureheaders = \
    cherrypy.Tool('before_finalize', secureheaders, priority=60)

Users = {'comsyslab': 'SecureAF'}

cherrypy.log.screen = False
"""
    Global cherrypy settings. 
    Set autoreload to True to allow reloading once python-files changed.
"""
conf = {
    'global': {
        'server.environment': 'production',
        'engine.autoreload.on': False,
        'engine.autoreload.frequency': 2,
        'server.socket_host': '0.0.0.0',  # Listen on any interface
        'server.socket_port': 8080,
        'server.ssl_module':'builtin',
        'server.ssl_certificate': os.path.abspath("certs/server.crt"),
        'server.ssl_private_key': os.path.abspath("certs/server.key")
    },
    '/': {
        'tools.secureheaders.on': True,
        'tools.auth_digest.on': True,
        'tools.auth_digest.realm': 'localhost',
        'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(Users),
        'tools.auth_digest.key': 'a5w8zc718d6c69fb',
        'tools.staticdir.root': os.path.abspath("www/")
    },
    '/static': {
        'tools.auth_digest.on': False,
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static/',
        'tools.caching.on': True,
        'tools.caching.delay': 3600,
        'tools.caching.antistampede_timeout': 1,
        'tools.gzip.on': True,
        'tools.gzip.mime_types': ['text/*', 'application/*']
    }
}

"""
   =========================
             Main
   =========================
"""


def check_python():
    python_Version = sys.version_info
    return python_Version.major >= 3 and python_Version.minor >= 4


def check_cherrypy():
    import importlib
    cp_loader = importlib.find_loader('cherrypy')
    if cp_loader is None:
        logging.info("Cherrypy is missing on this system. Please install cherrypy.")
        return False
    import cherrypy
    versParts = cherrypy.__version__.split('.')
    versParts = [int(x) for x in versParts]
    if versParts[0] < 3 or versParts[1] < 6:
        logging.info("Cherrypy is older then version 3.6. Please install version 3.6.0 or equivalent. (Currently: " + cherrypy.__version__ + ")")
        return False
    if versParts[0] > 3:
        logging.info("This application was developed with cherrypy v.3. Currently installed is " + cherrypy.__version__ + ". Full functionality cannot be guaranteed.")
    return True



"""
    Global index-class. Maps to root (localhost:8080/).
"""
class cIndex(object):

    switches = []

    def __init__(self):
        self.addSwitch('Tester', 1101)

    @cherrypy.expose
    def addSwitch(self, name, switchid):
        self.switches.append({'name': name, 'id': switchid})

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getSwitches(self):
        return self.switches

    @staticmethod
    @cherrypy.expose
    def index(**params):
        return serve_file(os.path.abspath('./www/index.html'), 'text/html')


def webInterface():
    logging.info("Starting Cherrypy-Engine")
    cherrypy.quickstart(gIndex, config=conf)


def shutdown():
    # shut webinterface down
    logging.info("Terminating queueThread")
    modules.gStations.queueThread.terminate()
    modules.gStations.measurement.watchDog.stop()
    logging.info("Saving Settings")
    settings.write("config/settings.json")
    logging.info("Shutting down Cherrypy-Engine")
    cherrypy.engine.exit()

if __name__ == '__main__':
    # Set root directory to script directory, to allow execution from anywhere
    # (Needs to happen before modules import, since __init__'s of some modules already use relative paths)
    scriptDir = os.path.dirname(sys.argv[0])
    logFile = "server.log"
    if scriptDir:
        logging.debug("Setting root dir to " + scriptDir)
        os.chdir(scriptDir)

    logging.info("Opening log-file: " + logFile)

    # Enable + configure logging
    logging.getLogger().setLevel(logging.INFO)

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-5.5s] [%(levelname)-5.5s] %(funcName)s : %(message)s")
    rootLogger = logging.getLogger()

    # Set the default logger to use our format
    for handler in rootLogger.handlers:
        handler.setFormatter(logFormatter)

    fileHandler = handlers.RotatingFileHandler(logFile, maxBytes=1024*1024*20, backupCount=1)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    if not check_python():
        logging.info("Python 3.4 or newer is required to run this application.")
        sys.exit()

    if not check_cherrypy():
        sys.exit()

    global gIndex
    gIndex = cIndex()

    # Suppress cherrypy's logging
    #cherrypy.log.error_log.propagate = False
    cherrypy.log.access_log.propagate = False

    logging.getLogger().setLevel(logging.DEBUG)

    Thread(target=webInterface).start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        shutdown()
