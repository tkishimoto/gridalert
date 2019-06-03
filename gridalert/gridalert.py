from logging import getLogger
logger = getLogger(__name__)

import cherrypy
import configparser
from itertools import product
from pathlib import Path

from .data_converter import *
from .label_helper import *
from .text_vectorizer import *
from .vector_cluster import *
from .plot_helper import *
from .data_visualizer import *
from .html_helper import *
from .anomaly_alert import *

from .const import Const as const

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

            logger.info('%s:%s is overwritten to %s' % (keys.split(':')[0],
                                                        keys.split(':')[1],
                                                        value)) 


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
        
            params = []
            for param in const.MLPARAMS:
                params.append(self.conf[cluster][param].split(','))

            tv = TextVectorizer(self.conf, cluster)
            vc = VectorCluster(self.conf, cluster)

            total = 0  
            for param in product(*params):
                total += 1

            counter = 0
            for param in product(*params):
                for ii, value in enumerate(param):
                    self.conf.set(cluster,
                                  const.MLPARAMS[ii], 
                                  value)

                counter += 1
                logger.info('Hyper parameters (%s/%s):' % (counter, total))
                for ii, value in enumerate(param):
                    key = const.MLPARAMS[ii]
                    logger.info('%s : %s' % (key, self.conf[cluster][key]))

                tv.set_conf(self.conf, cluster)
                vc.set_conf(self.conf, cluster)

                tv.vectorize()
                vc.clustering()

            vc.show_accuracy()         


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

