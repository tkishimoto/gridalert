from logging import getLogger

logger = getLogger(__name__)

from ..util import date as util_date
from ..util import text as util_text
from ..util import hash as util_hash

class StsTemplate:

    def __init__(self, cl_conf):

        self.cl_conf = cl_conf


    def initialize(self):
        logger.info('load sts template')
 

    def execute(self, text):
        buffers = []

        for line in open(text, errors='replace'):
            # genre filename year score sentence1 sentence2
            meta = line.split('\t')

            # host, date, service, metadata, data, label
            host     = 'dummy'
            date     = '2019-08-16 17:23:48'
            service  = 'dummy'
            label    = '1'
            metadata = 'dummy' 
            data0     = meta[5]
            data1     = meta[6]

            if 'dev' in text:
                metadata = 'dev'
            elif 'test' in text:
                metadata = 'test'
            elif 'train' in text:
                metadata = 'train'

            buffers.append([host, date, service,
                            metadata, data0, label])

            buffers.append([host, date, service,
                            metadata, data1, label])

        return buffers

