from logging import getLogger

logger = getLogger(__name__)

import time
import subprocess

from .algorithm import *

from .sqlite3_helper import *

from .util import reader as util_reader
from .util import path as util_path


class StsSimilarity:

    def __init__(self, conf):

        self.conf = conf
        self.service = ''
        self.train = ''
        self.test = ''
        self.model_paths = ''

        # scan db
        self.scan_db    = []


    def similarity(self):

        conf = self.conf
        for service in conf['cl']['services'].split(','):
            self.service = service             

            if 'dev' in service:
                self.train = 'dev'
                self.test  = 'dev'
 
            elif 'train' in service:
                self.train = 'train'
                self.test  = 'train'

            elif 'test' in service:
                self.train = 'train'
                self.test  = 'test'

            self.model_paths = util_path.model_paths(conf['cl'], self.train)

            docs0 = []
            docs1 = []
            input = conf['cl']['sts_dir'] + '/sts-%s.csv' % self.test
            for line in open(input, errors='replace'):
                meta = meta = line.split('\t')
                docs0.append(meta[5])
                docs1.append(meta[6])

            vector_type = conf['cl']['vector_type'].capitalize() + 'Vector'
            vector_func = globals()[vector_type](conf['cl'])
            data = vector_func.get_similarity(docs0, docs1, self.model_paths['vec']) 

            
            output = conf['cl']['model_dir'] + '/sys-%s.txt' % self.test
            file = open(output, 'w')
            for score in data:
                file.write('%s\n' % score)
            file.close()

            perl = conf['cl']['sts_dir'] + '/correlation.pl'           
            result = subprocess.check_output(['perl', perl, input, output])
            result = result.decode()
            result = result.split()[1]

            scan_dict = {}
            scan_dict['service'] = self.service
            scan_dict['acc0'] = float(result)
            scan_dict['acc1'] = 0
            scan_dict['sort'] = float(result)

            params = {}
            for param in const.MLPARAMS:
                params[param] = conf['cl'][param]

            scan_dict['params'] = params

            self.scan_db.append(scan_dict)


    def get_accuracy(self):
        return self.scan_db
