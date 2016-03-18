#!/usr/bin/python

import json
import logging
import os
import os.path
import sys
import time
from logging import handlers
from threading import Thread

import cherrypy
from cherrypy.lib.static import serve_file


# Add some headers to ask browser for more secure page rendering
# https://cherrypy.readthedocs.org/en/3.3.0/progguide/security.html
def secureheaders():
    headers = cherrypy.response.headers
    headers['X-Frame-Options'] = 'DENY'
    headers['X-XSS-Protection'] = '1; mode=block'
    headers['Content-Security-Policy'] = "default-src='self'"
    #if (cherrypy.server.ssl_certificate != None and cherrypy.server.ssl_private_key != None):
    #    headers['Strict-Transport-Security'] = 'max-age=31536000' # one year
    
cherrypy.tools.secureheaders = \
    cherrypy.Tool('before_finalize', secureheaders, priority=60)

Users = {'volker': 'volker'}

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
        #'server.ssl_module':'builtin',
        #'server.ssl_certificate': os.path.abspath("certs/server.crt"),
        #'server.ssl_private_key': os.path.abspath("certs/server.key"),
        'tools.encode.text_only': False
    },
    '/': {
        #'tools.secureheaders.on': True,
        #'tools.auth_digest.on': True,
        #'tools.auth_digest.realm': 'localhost',
        #'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(Users),
        #'tools.auth_digest.key': 'a5w8zc718d6c69fb',
        'tools.secureheaders.on': False, #remove if using https
        'tools.auth_digest.on': False, #remove if using https
        'tools.staticdir.root': os.path.abspath("www/")
    },
    '/static': {
        'tools.auth_digest.on': False,
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static/',
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


# noinspection PyDeprecation
def check_cherrypy():
    import importlib
    cp_loader = importlib.find_loader('cherrypy')
    if cp_loader is None:
        logging.info("Cherrypy is missing on this system. Please install cherrypy.")
        return False
    import cherrypy
    versParts = cherrypy.__version__.split('.')
    versParts = [int(x) for x in versParts]
    if versParts[0] < 3 and versParts[1] < 6:
        logging.info("Cherrypy is older then version 3.6. Please install version 3.6.0 or equivalent. (Currently: " + cherrypy.__version__ + ")")
        return False
    if versParts[0] > 3:
        logging.info("This application was developed with cherrypy v.3. Currently installed is " + cherrypy.__version__ + ". Full functionality cannot be guaranteed.")
    return True



"""
    Global index-class. Maps to root (localhost:8080/).
"""
class cIndex(object):

    switches = {}
    executor = 'plug'
    housecode = '31'

    def __init__(self):
        self.load()

    def load(self):
        try:
            with open('settings.json', "r+") as jsonFile:
                settings = json.loads(jsonFile.read())
                self.switches = settings['switches']
                self.executor = settings['exec']
                self.housecode = settings['housecode']
        except IOError as e:
            logging.warning("No config file could be found.")
        except KeyError as e:
            logging.warning('One or more setting couldn\'t be found.')
        except ValueError as e:
            logging.error(e)
            logging.error("Syntax Error in config File. Will be overwritten on exit.")

    def save(self):
        logging.info('Saving...')
        vals = {
            'switches': self.switches,
            'housecode': self.housecode,
            'exec': self.executor
        }
        with open('settings.json', 'w') as outfile:
            json.dump(vals, outfile, indent=4, sort_keys=True)

    @cherrypy.expose
    def addSwitch(self, name, switchid):
        if name == "" or switchid == "":
            return "Invalid input."
        self.switches[switchid] = {'name': name, 'active': 0}


    @cherrypy.expose
    def setSwitch(self, switchid, active):
        logging.info("id=" + switchid)
        if not switchid in self.switches:
            return 'Invalid id.'
        self.switches[switchid]['active'] = int(active)
        call = './' + self.executor + ' ' + self.housecode + ' ' + switchid + ' ' + str(self.switches[switchid]['active'])
        logging.debug('Executing: ' + call)
        os.system(call)
        return "1"

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
    gIndex.save()
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
    cherrypy.log.access_log.propagate = False

    logging.getLogger().setLevel(logging.DEBUG)

    Thread(target=webInterface).start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        shutdown()
