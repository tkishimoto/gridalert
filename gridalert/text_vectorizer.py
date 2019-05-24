from logging import getLogger

logger = getLogger(__name__)

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from fastText import train_unsupervised

from .sqlite3_helper import *

from .util import text as util_text
from .util import reader as util_reader
from .util import path as util_path


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
            self.model_path = util_path.model_vec_path(self.cl_conf, service)

            db_type = self.db_conf['type']
            vector_type = self.cl_conf['vector_type']

            func = getattr(self, "%s_to_%s" % (db_type, vector_type), None)
            if func is not None:
                func()

            else:
                logger.info('%s to %s not supported' % (db_type, vector_type))


    def sqlite3_to_doc2vec(self):

        db = Sqlite3Helper(self.db_conf) 
        data, tags = util_reader.get_data_from_sqlite3(db, 
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)

        trainings = []       
        for doc, tag in zip(data, tags):

            doc = util_text.filter_doc(doc)

            trainings.append(TaggedDocument(words=doc.split(), 
                             tags=[tag]))
        
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


    def sqlite3_to_fasttext(self):

        db = Sqlite3Helper(self.db_conf) 
        data, tags = util_reader.get_data_from_sqlite3(db, 
                                                       'service="%s"' % self.service,
                                                       self.cl_conf)

        text_path = self.cl_conf['model_dir'] + '/fasttext.tmp'

        trainings = open(text_path, 'w')

        for doc, tag in zip(data, tags):

            doc = util_text.filter_doc(doc)

            trainings.write('%s\n' % doc)

        trainings.close()

        cl_conf = self.cl_conf
        model = train_unsupervised(text_path,
                        dim = int(cl_conf['vector_size']),
                        ws = int(cl_conf['vector_window']),
                        epoch = int(cl_conf['vector_epochs']),
                        minCount = int(cl_conf['vector_min_count']),
                        thread = int(cl_conf['vector_workers']))

        model.save_model(self.model_path)

