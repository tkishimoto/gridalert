from logging import getLogger

logger = getLogger(__name__)

import os

from .sqlite3_helper import *
from .util import hash as util_hash

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
        where = 'service="%s"' % self.service
        fields = db.select(where=where, base_match=self.cl_conf)

        data_dict = {} # {hash: [original, diff, label, [tags]]}

        for ii, field in enumerate(fields):
            tag   = field['tag']
            data  = field['data']
            diff  = field['diff']
            label = field['label']

            diff = diff.split('\n')[3:]
            diff = '\n'.join(diff)

            hash = util_hash.md5('dummy', 'dummy', 'dummy', diff)

            if hash in data_dict.keys():
                data_dict[hash][3].append(tag)
            else:
                data_dict[hash] = [data, diff, label, [tag]]

        counter = 1
        for hash, value in data_dict.items():

            os.system('clear')

            original = value[0]
            diff = value[1]
            label = value[2]
            tags = value[3]

            logger.info('Process (%s/%s) %s counts observed' % (counter,
                                                      len(data_dict.keys()),
                                                      len(tags)))                   
     
            logger.info('Original logs:')
            print(original)
            logger.info('Diff to normal logs:')
            print(diff)
            print('\n')

            print('New label (%s) :' % label)
            label = input()

            for tag in tags:

                update = 'label="%s"' % label
                where = 'tag="%s"' % tag

                db.update(update, where)

            counter += 1    
