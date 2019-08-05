from logging import getLogger

logger = getLogger(__name__)

import glob

from .sqlite3_helper import *
from .template import *

from .util import match as util_match
from .util import hash as util_hash

class DataConverter:

    def __init__(self, conf):

        self.conf      = conf


    def text_to_db(self):

        db_type = self.conf['db']['type'] 

        func = getattr(self, "text_to_%s" % db_type, None)
        if func is not None:
            func()

        else:
            logger.info('%s not supported' % db_type)
 

    def text_to_sqlite3(self): 

        conf = self.conf

        class_name = conf['cl']['text_type'].capitalize() + 'Template'
        template = globals()[class_name](conf)
        template.initialize()

        texts = glob.glob(conf['cl']['text_input'])
        logger.info('input texts: %s' % (conf['cl']['text_input']))
        logger.info('# of text samples: %s' % (len(texts)))

        db = Sqlite3Helper(conf) 
        db.create_table()

        buffers = []
        for ii, text in enumerate(texts):

            logger.info('process (%s/%s) %s' % (ii+1, len(texts), text))

            # template should return ['host', 'date', 
            #                         'service', 'metadata',]
            #                         'data', 'label'

            for buffer in template.execute(text):

                cluster  = conf['cl']['name']
                host     = buffer[const.LOGPARAMS.index('host')]
                date     = buffer[const.LOGPARAMS.index('date')]
                service  = buffer[const.LOGPARAMS.index('service')]
                data     = buffer[const.LOGPARAMS.index('data')]

                if not util_match.base_match(conf['cl'], cluster, host, date):
                    continue
     
                # tag
                tag = util_hash.md5([cluster,
                                     host, 
                                     str(date), 
                                     service, 
                                     data])
                buffer = [tag, cluster] + buffer 

                # prediction, feature, diff
                buffer = buffer + ['unkonwn', 'unkonwn', 'unkonwn']
                buffers.append(buffer)

        db.insert_many(buffers)
        db.close()
