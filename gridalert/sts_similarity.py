from logging import getLogger

logger = getLogger(__name__)

import time

from .sqlite3_helper import *

from .util import reader as util_reader
from .util import path as util_path


class StsSimilarity:

    def __init__(self, conf):

        self.conf = conf
        self.service = ''
        self.model_paths = ''


    def similarity(self):
        print ('test')
        return
