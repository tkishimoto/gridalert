from logging import getLogger

logger = getLogger(__name__)

import math
import time
import difflib
import shelve
import joblib
import numpy as np
from pprint import pformat

from .algorithm import *

from .sqlite3_helper import *
from .util import reader as util_reader
from .util import path as util_path
from .const import Const as const

class VectorCluster:

    def __init__(self, conf):

        self.conf       = conf

        self.service     = ''
        self.model_paths = ''

        self.time       = []

        # scan db
        self.scan_db    = []

   
    def clustering(self):
 
        conf = self.conf

        for service in conf['cl']['services'].split(','):
            self.service = service
            self.model_paths = util_path.model_paths(conf['cl'], service)

            start = time.time()

            db = Sqlite3Helper(conf)
            docs, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % service,
                                                       conf['cl'])
            db.close()

            vector_type = conf['cl']['vector_type'].capitalize() + 'Vector'
            vector_func = globals()[vector_type](conf['cl'])
            data = vector_func.get_vector(docs, self.model_paths['vec'])
            data = vector_func.add_dimensions(data, docs)

            cluster_type = conf['cl']['cluster_type'].capitalize() + 'Cluster'
            cluster_func = globals()[cluster_type](conf['cl'])
            pred_data = cluster_func.create_model(data, tags, self.model_paths['cls'])

            self.dump_to_db(tags, pred_data, data)

            elapsed_time = time.time() - start
            self.time.append({'service':service, 'time':elapsed_time})

            self.save_accuracy()

            if conf['cl']['use_diff'] == 'True':
                self.diff_anomaly()


    def dump_to_db(self, tags, pred_data, data):
        conf = self.conf

        labels = []
        means  = []
        for ii, pred in enumerate(pred_data):
            if pred != const.ABNORMAL:
                means.append(data[ii]) 

        if len(means) == 0:
            means.append([0]*len(data[0]))

        means = np.mean(np.array(means), axis=0)

        buffers = []

        for ii, features in enumerate(data):

            distance = 0
            for jj in range(len(means)):
                diff = features[jj] - means[jj]
                distance += diff*diff

            distance = math.sqrt(distance)

            feature = ''
            for jj in range(len(means)):
                feature += 'feature%s=%s,' % (jj, data[ii][jj])

            feature += 'distance=%s' % distance

            # 'tag', 'host', 'date', 'prediction', 'feature', 'diff'
            tag = tags[ii]
            prediction = pred_data[ii]
            buffers.append([str(prediction), feature, tag])

        if self.conf['cl']['use_prediction'] == 'True':
            update = 'prediction=?,feature=?'
            where = 'tag=?'

            db = Sqlite3Helper(conf)
            db.create_table()

            db.update_many(update, where, buffers)
            db.close()

        # shelve
        shelve_db = shelve.open(self.model_paths['result'])
        for buffer in buffers:
            shelve_db[buffer[2]] = {'prediction':buffer[0]}
        shelve_db.close()


    def save_accuracy(self):
        conf = self.conf 

        shelve_db = shelve.open(self.model_paths['result'])

        den0, den1 = 0., 0.
        num0, num1 = 0., 0.

        for key in shelve_db:
            db = Sqlite3Helper(conf)
            field = db.select(where='tag="%s"' % key)
            label = field[0]['label']

            if label != str(const.ABNORMAL):
                den1 += 1

                if shelve_db[key]['prediction'] != str(const.ABNORMAL):
                    num1 += 1

            else:
                den0 += 1

                if shelve_db[key]['prediction'] == str(const.ABNORMAL):
                    num0 += 1

            db.close()

        acc0 = '0'
        acc1 = '0'

        if den0 > 0:
            acc0 = num0/den0

        if den1 > 1:
            acc1 = num1/den1

        logger.info('RESULTS: %s %s' % (conf['cl']['name'], self.service))
        logger.info('RESULTS: accuracy of normal events (pred/pre-label): %s/%s = %s' % (num1,
                                                               den1,
                                                               acc1))
        logger.info('RESULTS: accuracy of anomaly events (pred/pre-label): %s/%s = %s' % (num0,
                                                               den0,
                                                               acc0))

        scan_dict = {}
        scan_dict['service'] = self.service
        scan_dict['acc0'] = float(acc0)
        scan_dict['acc1'] = float(acc1)
        scan_dict['sort'] = float(acc1) + float(acc0)

        params = {}
        for param in const.MLPARAMS:
            params[param] = conf['cl'][param]
      
        scan_dict['params'] = params
 
        self.scan_db.append(scan_dict)
     
   
    def get_accuracy(self):
        return self.scan_db


    def diff_anomaly(self):
        db = Sqlite3Helper(conf)
        fields = db.select(where='service="%s"' % self.service,
                           base_match=conf['cl'])
        db.close()


        center = fields[0]
        distance = const.INVALID

        for field in fields:
            feature = field['feature']

            if not 'distance' in feature: 
                continue

            data = {}
            for index in feature.split(','):
                data[index.split('=')[0]] = index.split('=')[1]

            if float(data['distance']) < distance:
                distance = float(data['distance'])
                center = field

        buffers = []

        for field in fields:
            diff = difflib.unified_diff(center['data'].splitlines(),
              field['data'].splitlines(),
              'normal event',
              'anomaly event',
              '%s %s %s' % (center['host'],
                            self.service,
                            center['date']),
              '%s %s %s' % (field['host'],
                            self.service,
                            field['date']))

            diff = '\n'.join(diff)
            diff = diff.replace('"', '')

            buffers.append([diff, field['tag']])

        update = 'diff=?'
        where = 'tag=?'

        db = Sqlite3Helper(conf)
        db.update_many(update, where, buffers)
        db.close()

    def get_time(self):
        return self.time

