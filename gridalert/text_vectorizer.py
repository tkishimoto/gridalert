from logging import getLogger

logger = getLogger(__name__)

import time

from .algorithm import *
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

            db = Sqlite3Helper(self.db_conf)
            data, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % service,
                                                       self.cl_conf)
            db.close() 

            if len(data) == 0:
                logger.info('No data are selected.')
                return

            vector_type = self.cl_conf['vector_type'].capitalize() + 'Vector'
            vector_func = globals()[vector_type](self.cl_conf)
            vector_func.create_model(data, tags, self.model_path)

            elapsed_time = time.time() - start
            self.time.append({'service':service, 'time':elapsed_time})

