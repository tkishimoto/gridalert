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
 

    def execute(self, lines):
        buffers = []

        for line in lines:
            print (line)

        return buffers

