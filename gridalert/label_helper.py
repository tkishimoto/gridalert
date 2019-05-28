from logging import getLogger

logger = getLogger(__name__)

import os

from .sqlite3_helper import *

class LabelHelper:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]

        self.service    = ''


    def labeling(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service
        
            db_type = self.db_conf['type']

            func = getattr(self, "label_%s" % db_type, None)
            if func is not None:
                func()

            else:
                logger.info('%s not supported' % db_type)
                        
   
    def label_sqlite3(self):
        db   = Sqlite3Helper(self.db_conf)
        where = 'service="%s" and diff!=""' % self.service
        fields = db.select(where=where, base_match=self.cl_conf)

        for ii, field in enumerate(fields):
            os.system('clear')

            tag  = field['tag']
            host = field['host']
            date = field['date']
            label = field['label']
            data = field['data']
            diff = field['diff']

            logger.info('Process (%s/%s) %s %s %s' % (ii+1,
                                                      len(fields),
                                                      host, 
                                                      self.service, date))                   
     
            logger.info('Original logs:')
            print(data)
            logger.info('Diff to normal logs:')
            print(diff)
            print('\n')

            print('New label (%s) :' % label)
            label = input()

            update = 'label="%s"' % label
            where = 'tag="%s"' % tag

            db.update(update, where)


