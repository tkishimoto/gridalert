from logging import getLogger

logger = getLogger(__name__)

from gensim.models import Word2Vec

from .util import text as util_text

class ScdvHelper:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]


    def word2vec(self, data):
        docs = []

        for doc in data:
            if self.cl_conf['vector_jp_num'] == 'True':
                doc = util_text.filter_doc(doc)

            docs.append(doc.split())

        cl_conf = self.cl_conf
        model = Word2Vec(docs, 
                         workers=int(cl_conf['vector_workers']), 
                         hs = int(cl_conf['vector_hs']), 
                         negative = int(cl_conf['vector_negative']), 
                         iter = int(cl_conf['vector_epochs']),
                         size=int(cl_conf['vector_size']), 
                         min_count=int(cl_conf['vector_min_count']), 
                         window=int(cl_conf['vector_window']), 
                         sample=float(cl_conf['vector_sample']), 
                         seed=int(cl_conf['vector_seed']))


        model.init_sims(replace=True)
        return model
