from logging import getLogger

logger = getLogger(__name__)

import time

from .algorithm import *
from .sqlite3_helper import *

from .util import reader as util_reader
from .util import path as util_path


class TextVectorizer:

    def __init__(self, conf):

        self.conf = conf
        self.service = ''
        self.model_paths = ''

        self.time = []

   
    def vectorize(self):

        conf = self.conf 

        for service in conf['cl']['services'].split(','):
            self.service = service
            self.model_paths = util_path.model_paths(self.conf['cl'], service)

            start = time.time()  

            db = Sqlite3Helper(conf)
            data, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % service,
                                                       conf['cl'])
            db.close() 

            if len(data) == 0:
                logger.info('No data are selected.')
                return

            vector_type = conf['cl']['vector_type'].capitalize() + 'Vector'
            vector_func = globals()[vector_type](conf['cl'])
            vector_func.create_model(data, tags, self.model_paths['vec'])

            elapsed_time = time.time() - start
            self.time.append({'service':service, 'time':elapsed_time})

    def get_time(self):
        return self.time
