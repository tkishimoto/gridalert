from logging import getLogger
logger = getLogger(__name__)

import configparser

from .data_converter import *
from .text_vectorizer import *
from .vector_cluster import *
from .data_visualizer import *
from .anomaly_alert import *

class GridAlert:

    def __init__(self, conf):

        self.clusters = []

        for cluster in conf.sections():
            if 'cluster/' in cluster:
                self.clusters.append(cluster)

        self.conf = conf


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

