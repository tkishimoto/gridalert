from logging import getLogger
from logging import basicConfig

logger = getLogger(__name__)

import cherrypy
import configparser
from pathlib import Path

from .data_converter import *
from .label_helper import *
from .text_vectorizer import *
from .vector_cluster import *
from .data_visualizer import *
from .anomaly_alert import *
from .scan_helper import *

from .const import Const as const
from .util import hash as util_hash

class GridAlert:

    def __init__(self, conf='', options=''):

        # config parser
        cwd = Path(__file__).parent

        default = configparser.ConfigParser()
        default.read('%s/default.conf' % cwd)

        myconf = self.read_file_conf(default, conf)
        myconf = self.read_option_conf(myconf, options)
                    
        clusters = []
        self.conf = {}

        for section in myconf.sections():
            if 'cluster/' in section:
                clusters.append(section)

            self.conf[section] = myconf[section]
        
        self.conf['DEFAULT'] = myconf['DEFAULT']
        self.conf['clusters'] = clusters
        logger.info('clusters: %s is defined' % clusters) 

        # logger
        basicConfig(level=const.LOG_LEVEL[int(self.conf['DEFAULT']['log_level'])],
            format='%(asctime)s [%(levelname)-7s] %(message)s')


    def read_file_conf(self, default, conf):
        if conf:
            if Path(conf).is_absolute():
                default.read(conf)
            else:
                default.read('%s/%s' % (Path.cwd(), conf))

        return default


    def read_option_conf(self, default, options):
        for option in options.split(','):
            if not '=' in option:
                continue

            keys = option.split('=')[0]
            value = option.split('=')[1]
        
            default.set(keys.split(':')[0], 
                        keys.split(':')[1], 
                        value) 

            logger.warn('%s:%s is overwritten to %s' % (keys.split(':')[0],
                                                        keys.split(':')[1],
                                                        value)) 
        return default


    # main grid alert methos 

    def text_to_db(self):
        for cluster in self.conf['clusters']:
            self.conf['cl'] = self.conf[cluster]
            dc = DataConverter(self.conf)
            dc.text_to_db()

    def labeling(self):
        for cluster in self.clusters:
            lh = LabelHelper(self.conf, cluster)
            lh.labeling()

    def vectorize(self):
        for cluster in self.conf['clusters']:
            self.conf['cl'] = self.conf[cluster]
            tv = TextVectorizer(self.conf)
            tv.vectorize()
   
 
    def clustering(self):
        for cluster in self.conf['clusters']:
            self.conf['cl'] = self.conf[cluster]
            vc = VectorCluster(self.conf)
            vc.clustering()

   
    def scan(self):
        for cluster in self.clusters:
            sh = ScanHelper(self.conf, cluster)   
            sh.scan()     

    def plot(self):
        for cluster in self.conf['clusters']:
            self.conf['cl'] = self.conf[cluster]
            aa = AnomalyAlert(self.conf)
            aa.predict()
            aa.plot()

    def visualize(self):
        conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': Path.cwd()
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': self.conf['DEFAULT']['base_dir']
            },
            'global': {
                'server.socket_host':'0.0.0.0'
            }
        }
 
        dv = DataVisualizer(self.conf)
        cherrypy.quickstart(dv, '/', conf)


    def alert(self):
        contents = ''

        for cluster in self.conf['clusters']:
            self.conf['cl'] = self.conf[cluster]
            aa = AnomalyAlert(self.conf)
            aa.predict()
            contents += aa.alert()

        aa.alert_anomaly(contents)
