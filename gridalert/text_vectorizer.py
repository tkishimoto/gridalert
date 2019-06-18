from logging import getLogger

logger = getLogger(__name__)

import time

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

        self.time = []

   
    def vectorize(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service
            self.model_path = util_path.model_vec_path(self.cl_conf, service)

            start = time.time()  

            db_type = self.db_conf['type']
            db_func = getattr(self, "get_data_from_%s" % (db_type), None)
            data, tags = db_func()

            if len(data) == 0:
                logger.info('No data are selected.')
                return

            vector_type = self.cl_conf['vector_type']
            vector_func = getattr(self, "vectorize_%s" % (vector_type), None)
            vector_func(data, tags)

            elapsed_time = time.time() - start
            self.time.append({'service':service, 'time':elapsed_time})

 
    def get_time(self):
        return self.time


    def get_data_from_sqlite3(self):
 
        db = Sqlite3Helper(self.db_conf) 
        data, tags = util_reader.get_data_from_sqlite3(db, 
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)
        db.close() 
        return data, tags


    def vectorize_doc2vec(self, data, tags):

        trainings = []       
        for doc, tag in zip(data, tags):

            if self.cl_conf['vector_jp_num'] == 'True':
                doc = util_text.filter_doc(doc)

            trainings.append(TaggedDocument(words=doc.split(), 
                             tags=[tag]))
        
        cl_conf = self.cl_conf
        model = Doc2Vec(documents = trainings, 
                        dm = int(cl_conf['vector_dm']), 
                        vector_size = int(cl_conf['vector_size']), 
                        window = int(cl_conf['vector_window']), 
                        alpha = float(cl_conf['vector_alpha']), 
                        min_alpha = float(cl_conf['vector_min_alpha']), 
                        seed = int(cl_conf['vector_seed']),
                        min_count = int(cl_conf['vector_min_count']), 
                        sample = float(cl_conf['vector_sample']), 
                        workers = int(cl_conf['vector_workers']),
                        epochs = int(cl_conf['vector_epochs']),
                        hs = int(cl_conf['vector_hs']),
                        negative = int(cl_conf['vector_negative']),
                        ns_exponent = float(cl_conf['vector_ns_exponent']),
                        dm_mean = int(cl_conf['vector_dm_mean']),
                        dm_concat = int(cl_conf['vector_dm_concat']),
                        dm_tag_count = int(cl_conf['vector_dm_tag_count']),
                        dbow_words = int(cl_conf['vector_dbow_words'])) 

        model.save(self.model_path)


    def vectorize_fasttext(self, data, tags):

        text_path = self.cl_conf['model_dir'] + '/fasttext.tmp'

        trainings = open(text_path, 'w', errors='replace')

        for doc, tag in zip(data, tags):

            if self.cl_conf['vector_jp_num'] == 'True':
                doc = util_text.filter_doc(doc)

            trainings.write('%s\n' % doc)

        trainings.close()

        cl_conf = self.cl_conf
        verbose = 2
        if int(cl_conf['log_level']) <= 1:
            verbose = 0

        model = train_unsupervised(text_path,
                        model = cl_conf['vector_model'],
                        lr = float(cl_conf['vector_alpha']),
                        dim = int(cl_conf['vector_size']),
                        ws = int(cl_conf['vector_window']),
                        epoch = int(cl_conf['vector_epochs']),
                        minCount = int(cl_conf['vector_min_count']),
                        minCountLabel = int(cl_conf['vector_min_count_label']),
                        minn = int(cl_conf['vector_minn']),
                        maxn = int(cl_conf['vector_maxn']),
                        neg = int(cl_conf['vector_negative']),
                        wordNgrams = int(cl_conf['vector_word_ngrams']),
                        loss = cl_conf['vector_loss'],
                        bucket = int(cl_conf['vector_bucket']),
                        lrUpdateRate = int(cl_conf['vector_lr_update_rate']),
                        thread = int(cl_conf['vector_workers']),
                        t = float(cl_conf['vector_sample']),
                        verbose = verbose)

        model.save_model(self.model_path)

