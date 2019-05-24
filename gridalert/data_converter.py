from logging import getLogger

logger = getLogger(__name__)

import glob

from .sqlite3_helper import *
from .template import *

from .util import match as util_match
from .util import date as util_date

class DataConverter:

    def __init__(self, conf, cluster):

        self.conf      = conf
        self.cluster   = cluster

        self.db_conf = conf['db']
        self.cl_conf = conf[cluster]


    def text_to_db(self):

        db_type = self.db_conf['type'] 

        func = getattr(self, "text_to_%s" % db_type, None)
        if func is not None:
            func()

        else:
            logger.info('%s not supported' % db_type)
 

    def text_to_sqlite3(self): 

        class_name = self.cl_conf['text_type'].capitalize() + 'Template'
        template = globals()[class_name](self.cl_conf)
        template.initialize()

        texts = glob.glob(self.cl_conf['text_input'])
        logger.info('input texts: %s' % (self.cl_conf['text_input']))
        logger.info('# of text samples: %s' % (len(texts)))

        db = Sqlite3Helper(self.db_conf) 
        db.create_table()

        buffers = []
        for ii, text in enumerate(texts):

            logger.info('process (%s/%s) %s' % (ii+1, len(texts), text))

            lines = open(text).readlines()

            for buffer in template.execute(lines):

                if util_match.base_match(self.cl_conf, 
                    buffer[const.DB_COLUMN_NAMES.index('cluster')], 
                    buffer[const.DB_COLUMN_NAMES.index('host')], 
                    buffer[const.DB_COLUMN_NAMES.index('date')]):
        
                    # prediction, feature, diff
                    buffer = buffer + ['unkonwn', 'unkonwn', 'unkonwn']

                    buffers.append(buffer)

        db.insert_many(buffers)
        db.close()
