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
from .plot_helper import *
from .data_visualizer import *
from .html_helper import *
from .anomaly_alert import *
from .scan_helper import *

from .const import Const as const
from .util import hash as util_hash

class GridAlert:

    def __init__(self, conf='', options=''):

        cwd = Path(__file__).parent

        default = configparser.ConfigParser()
        default.read('%s/default.conf' % cwd)

        if conf:
            if Path(conf).is_absolute():
                default.read(conf)
            else:
                default.read('%s/%s' % (Path.cwd(), conf))
                    
        for option in options.split():
            keys = option.split('=')[0]
            value = option.split('=')[1]
        
            default.set(keys.split(':')[0], 
                        keys.split(':')[1], 
                        value) 

            logger.warn('%s:%s is overwritten to %s' % (keys.split(':')[0],
                                                        keys.split(':')[1],
                                                        value)) 

        # logger
        basicConfig(level=const.LOG_LEVEL[int(default['DEFAULT']['loglevel'])],
            format='%(asctime)s [%(levelname)-7s] %(message)s')

        self.clusters = []

        for cluster in default.sections():
            if 'cluster/' in cluster:
                self.clusters.append(cluster)

        default.set('DEFAULT', 'clusters', ','.join(self.clusters)) 

        logger.info('clusters: %s is defined' % self.clusters) 

        self.conf = default


    def text_to_db(self):
        for cluster in self.clusters:
            dc = DataConverter(self.conf, cluster)
            dc.text_to_db()

    def labeling(self):
        for cluster in self.clusters:
            lh = LabelHelper(self.conf, cluster)
            lh.labeling()

    def vectorize(self):
        for cluster in self.clusters:
            tv = TextVectorizer(self.conf, cluster)
            tv.vectorize()
   
 
    def clustering(self):
        for cluster in self.clusters:
            vc = VectorCluster(self.conf, cluster)
            vc.clustering()

   
    def scan(self):
        for cluster in self.clusters:
            sh = ScanHelper(self.conf, cluster)   
            sh.scan()     

    def plot(self):
        for cluster in self.clusters:
            ph = PlotHelper(self.conf, cluster)
            ph.plot()

 
    def html(self):
        hh = HtmlHelper(self.conf)
        hh.make_html(self.conf)


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
        aa = AnomalyAlert(self.conf)
        aa.send_mail()

