from logging import getLogger

logger = getLogger(__name__)

import os

from .sqlite3_helper import *
from .util import hash as util_hash

class LabelHelper:

    def __init__(self, conf):

        self.conf       = conf
        self.service    = ''


    def labeling(self):
        db   = Sqlite3Helper(self.conf)
        where = 'service="%s"' % self.service
        results = db.select(where=where)
  
        fields = []
        for result in results:
            if util_match.base_match_wo_cluster(self.conf['cl'],
                                         result['host'],
                                         result['date']):
                fields.append(result)

        data_dict = {} # {hash: [original, diff, label, [tags]]}

        for ii, field in enumerate(fields):
            tag   = field['tag']
            data  = field['data']
            diff  = field['diff']
            label = field['label']

            hash = util_hash.md5([data])

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

            logger.info('Process cluster : %s' % self.conf['cl']['name'])
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

            buffers = []
            for tag in tags:
                buffers.append([label, tag])

            update = 'label=?'
            where = 'tag=?'

            db.update_many(update, where, buffers)

            counter += 1    
