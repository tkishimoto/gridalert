from logging import getLogger

logger = getLogger(__name__)

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from .sqlite3_helper import *

from .util import text as util_text


class TextVectorizer:

    def __init__(self, conf, index):
        self.conf      = conf
        self.index     = index
        self.db_conf   = conf.db_conf
        self.base_conf = conf.base_confs[index]
        self.tv_conf   = conf.tv_confs[index]

        self.service = ''
        self.path    = ''

        self.conf = conf


    def initialize(self):

        work_dir = self.conf.work_dir

        if not self.db_conf.path:
            self.db_conf.path = work_dir + '/database.db'

        if not self.tv_conf.dir:
            self.tv_conf.dir = work_dir


    def vectorize(self):

        for service in self.base_conf.services:
            self.service = service

            model = '%s.%s.vec.model' % (self.base_conf.name,
                                            self.service)
            self.path = self.tv_conf.dir + '/' + model

            if self.db_conf.type == 'sqlite3':
                if self.tv_conf.type == 'doc2vec':
                    self.sqlite3_to_doc2vec()
                else:
                    logger.info('%s not supported' % (self.tv_conf.type))
            else:
                logger.info('%s not supported' % (self.db_conf.type))


    def sqlite3_to_doc2vec(self):
        tv_conf = self.tv_conf

        db = Sqlite3Helper(self.conf, self.index) 
        fields = db.select_data_service(self.service)

        logger.info('total samples : %s' % (len(fields)))

        if (len(fields) <= 0):
            logger.info('no trainig data')
            return 

        trainings = []       
        for counter, docs in enumerate(fields):

            data = docs['data']
            data = util_text.filter_doc(data)

            trainings.append(TaggedDocument(words=data.split(), 
                             tags=[docs['tag']]))
        
        model = Doc2Vec(documents = trainings, 
                        dm = tv_conf.dm, 
                        vector_size = tv_conf.vector_size, 
                        window = tv_conf.window, 
                        min_count = tv_conf.min_count, 
                        workers = tv_conf.workers,
                        epochs = tv_conf.epochs,
                        seed = tv_conf.seed) 

        model.save(self.path)

