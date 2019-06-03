from logging import getLogger

logger = getLogger(__name__)

from ..util import date as util_date
from ..util import text as util_text
from ..util import hash as util_hash

class MessagesTemplate:

    def __init__(self, cl_conf):

        self.cl_conf = cl_conf


    def initialize(self):
        logger.info('load messages template')
 

    def execute(self, text):
        buffers = []

        for line in open(text):
            #  May 13 03:10:01 localhost data
            meta = line.split()

            # tag, cluster, host, date, service, metadata, data, label
            cluster  = self.cl_conf['name']
            host     = meta[3]
            date     = util_date.sysdate_to_sqdate('%s %s %s 2019' % (meta[0], 
                                                                      meta[1], 
                                                                      meta[2]))
            service  = meta[4].replace(':', '')
            if not service in self.cl_conf['services'].split(','):
                continue
           
            metadata = 'nothing'
            label    = '1'
            data     = ' '.join(meta[5:])

            tag      = util_hash.md5(cluster, host, str(date), data)
        
            buffers.append([tag, cluster, host, date, service,
                            metadata, data, label])

        return buffers

