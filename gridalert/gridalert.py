from logging import getLogger

logger = getLogger(__name__)

from .data_converter import *
from .text_vectorizer import *
from .vector_cluster import *
from .data_visualizer import *

class GridAlert:

    def __init__(self, conf):

        self.conf = conf


    def text_to_db(self):
        names = self.conf.get_base_names()

        for ii, name in enumerate(names):
            dc = DataConverter(self.conf, ii)
            dc.initialize()
            dc.text_to_db()


    def vectorize(self):
        names = self.conf.get_base_names()

        for ii, name in enumerate(names):
            tv = TextVectorizer(self.conf, ii)
            tv.initialize()
            tv.vectorize()
    

    def clustering(self):
        names = self.conf.get_base_names()

        for ii, name in enumerate(names):
            vc = VectorCluster(self.conf, ii)
            vc.initialize()
            vc.clustering()
    

    def visualize(self):
        names = self.conf.get_base_names()

        for ii, name in enumerate(names):
            dv = DataVisualizer(self.conf, ii)
            dv.initialize()
            dv.visualize()

