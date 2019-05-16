from logging import getLogger

logger = getLogger(__name__)

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from .sqlite3_helper import *

from .util import text as util_text


class TextVectorizer:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]

        self.service    = ''
        self.model_path = ''

    def vectorize(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service

            model = '%s.%s.vec.model' % (self.cl_conf['name'],
                                         self.service)
            self.model_path = self.cl_conf['model_dir'] + '/' + model

            if self.db_conf['type'] == 'sqlite3':
                if self.cl_conf['vector_type'] == 'doc2vec':
                    self.sqlite3_to_doc2vec()
                else:
                    logger.info('%s not supported' % (self.cl_conf['vector_type']))
            else:
                logger.info('%s not supported' % (self.db_conf['type']))


    def sqlite3_to_doc2vec(self):

        db = Sqlite3Helper(self.db_conf) 
        fields = db.select(where='service="%s"' % self.service)

        if (len(fields) <= 0):
            logger.info('no trainig data')
            return 

        logger.info('total samples : %s' % (len(fields)))

        trainings = []       
        for counter, docs in enumerate(fields):

            data = docs['data']
            data = util_text.filter_doc(data)

            trainings.append(TaggedDocument(words=data.split(), 
                             tags=[docs['tag']]))
        
        cl_conf = self.cl_conf
        model = Doc2Vec(documents = trainings, 
                        dm = int(cl_conf['vector_dm']), 
                        vector_size = int(cl_conf['vector_size']), 
                        window = int(cl_conf['vector_window']), 
                        min_count = int(cl_conf['vector_min_count']), 
                        workers = int(cl_conf['vector_workers']),
                        epochs = int(cl_conf['vector_epochs']),
                        seed = int(cl_conf['vector_seed'])) 

        model.save(self.model_path)

