from logging import getLogger

logger = getLogger(__name__)

import os
import glob

from .sqlite3_helper import *
from .template import *

from .util import match as util_match
from .util import date as util_date

class DataConverter:

    def __init__(self, conf, index):

        self.conf      = conf
        self.index     = index
        self.db_conf   = conf.db_conf
        self.base_conf = conf.base_confs[index]
        self.dc_conf   = conf.dc_confs[index]


    def initialize(self):

        work_dir = self.conf.work_dir

        if not self.db_conf.path:
            self.db_conf.path = work_dir + '/database.db'


    def text_to_db(self):

        if self.db_conf.type == 'sqlite3':
            self.text_to_sqlite3()

        else:
            logger.info('%s not supported' % (self.dc_conf.db_type))
 

    def text_to_sqlite3(self): 
        dc_conf = self.dc_conf
        db_conf = self.db_conf
        base_conf = self.base_conf

        class_name = dc_conf.text_type.capitalize() + 'Template'
        template = globals()[class_name](self.conf, self.index)
        template.initialize()

        texts = glob.glob(dc_conf.text_path)
        exists = os.path.exists(db_conf.path)

        db = Sqlite3Helper(self.conf, self.index) 
        db.create_table()

        buffers = []
        for ii, text in enumerate(texts):

            logger.info('process (%s/%s) %s' % (ii+1, len(texts), text))

            lines = open(text).readlines()

            for buffer in template.execute(lines):

                if util_match.base_match(base_conf, 
                    buffer[db_conf.get_data_index("host")], 
                    buffer[db_conf.get_data_index("date")]):
        
                    # prediction, feature, diff
                    buffer = buffer + ['unkonwn', 'unkonwn', 'unkonwn']

                    buffers.append(buffer)

        db.insert_many(buffers)
        db.close()
