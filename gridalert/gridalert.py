from logging import getLogger
logger = getLogger(__name__)

import configparser
from pathlib import Path

from .data_converter import *
from .text_vectorizer import *
from .vector_cluster import *
from .data_visualizer import *
from .anomaly_alert import *

class GridAlert:

    def __init__(self, conf=''):
        cwd = Path(__file__).parent

        default = configparser.ConfigParser()
        default.read('%s/default.conf' % cwd)

        if conf:
            if Path(conf).is_absolute():
                default.read(conf)
            else:
                default.read('%s/%s' % (Path.cwd(), conf))
                    
        self.clusters = []

        for cluster in default.sections():
            if 'cluster/' in cluster:
                self.clusters.append(cluster)

        default.set('DEFAULT', 'clusters', ','.join(self.clusters)) 

        self.conf = default


    def text_to_db(self):
        for cluster in self.clusters:
            dc = DataConverter(self.conf, cluster)
            dc.text_to_db()


    def vectorize(self):
        for cluster in self.clusters:
            tv = TextVectorizer(self.conf, cluster)
            tv.vectorize()
   
 
    def clustering(self):
        for cluster in self.clusters:
            vc = VectorCluster(self.conf, cluster)
            vc.clustering()
  
 
    def visualize(self):
        for cluster in self.clusters:
            dv = DataVisualizer(self.conf, cluster)
            dv.visualize()

        dv = DataVisualizer(self.conf)
        dv.make_top_html()


    def alert(self):
        aa = AnomalyAlert(self.conf)
        aa.send_mail()

