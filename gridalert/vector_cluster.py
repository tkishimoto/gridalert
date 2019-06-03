from logging import getLogger

logger = getLogger(__name__)

import math
import pickle
import difflib
import shelve
import numpy as np
from pprint import pformat

from gensim.models.doc2vec import Doc2Vec
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN

from .sqlite3_helper import *
from .util import reader as util_reader
from .util import path as util_path
from .const import Const as const

class VectorCluster:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]

        self.service    = ''
        self.model_vec_path = ''
        self.model_cls_path = ''
        self.model_result_path = ''

        # scan db
        self.scan_db    = []

   
    def set_conf(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']    
        self.cl_conf    = conf[cluster]


    def clustering(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service
            self.model_vec_path = util_path.model_vec_path(self.cl_conf, service)
            self.model_cls_path = util_path.model_cls_path(self.cl_conf, service)
            self.model_result_path = util_path.model_result_path(self.cl_conf, service)

            vector_type = self.cl_conf['vector_type']
            vector_func = getattr(self, "get_data_from_%s" % (vector_type), None)
            data, tags = vector_func()

            cluster_type = self.cl_conf['cluster_type']
            cluster_func = getattr(self, "cluster_%s" % (cluster_type), None)
            cluster_func(data, tags)

            self.save_accuracy()

            if self.cl_conf['use_diff'] == 'True':
                self.diff_anomaly()


    def get_data_from_doc2vec(self):
 
        db = Sqlite3Helper(self.db_conf)
        docs, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)
  
        data = util_reader.get_data_from_doc2vec(self.model_vec_path, docs, self.cl_conf)
        return data, tags


    def get_data_from_fasttext(self):
 
        db = Sqlite3Helper(self.db_conf)
        docs, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)
 
        data = util_reader.get_data_from_fasttext(self.model_vec_path, docs, self.cl_conf)
        return data, tags


    def cluster_isolationforest(self, data, tags):
        data = np.array(data)

        cl_conf = self.cl_conf
        model = IsolationForest(behaviour=cl_conf['cluster_behaviour'],
                                n_estimators=int(cl_conf['cluster_n_estimators']),
                                contamination=cl_conf['cluster_contamination'],
                                random_state=int(cl_conf['cluster_random_state']),
                                max_samples=int(cl_conf['cluster_max_samples']),
                                n_jobs=int(cl_conf['cluster_n_jobs']))
        model.fit(data)
        pred_data = model.predict(data)

        self.dump_to_db(tags, pred_data, data)          
 
        pickle.dump(model, open(self.model_cls_path, 'wb'))


    def cluster_dbscan(self, data, tags):
        data = np.array(data)

        cl_conf = self.cl_conf
        model = DBSCAN(eps=float(cl_conf['cluster_eps']),
                       min_samples=int(cl_conf['cluster_min_samples']),
                       n_jobs=int(cl_conf['cluster_n_jobs']))
        model.fit(data)
        pred_data = model.labels_
        self.dump_to_db(tags, pred_data, data)          
 
        pickle.dump(model, open(self.model_cls_path, 'wb'))


    def dump_to_db(self, tags, pred_data, data):
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

            label = ''
            for jj in range(len(means)):
                label += 'feature%s=%s,' % (jj, data[ii][jj])

            label += 'distance=%s' % distance

            # 'tag', 'host', 'date', 'prediction', 'feature', 'diff'
            tag = tags[ii]
            prediction = pred_data[ii]
            buffers.append([str(prediction), label, tag])

        update = 'prediction=?,feature=?'
        where = 'tag=?'

        db = Sqlite3Helper(self.db_conf)
        db.create_table()

        db.update_many(update, where, buffers)

        # shelve
        shelve_db = shelve.open(self.model_result_path)
        for buffer in buffers:
            shelve_db[buffer[2]] = {'label': buffer[1],
                                    'prediction':buffer[0]}
        shelve_db.close()


    def save_accuracy(self):
        shelve_db = shelve.open(self.model_result_path)

        den0, den1 = 0., 0.
        num0, num1 = 0., 0.

        for key in shelve_db:
            if shelve_db[key]['label'] != str(const.ABNORMAL):
                den1 += 1

                if shelve_db[key]['prediction'] != str(const.ABNORMAL):
                    num1 += 1

            else:
                den0 += 1

                if shelve_db[key]['prediction'] == str(const.ABNORMAL):
                    num0 += 1

        acc0 = '0'
        acc1 = '0'

        if den0 > 0:
            acc0 = num0/den0

        if den1 > 1:
            acc1 = num1/den1

        logger.info('RESULTS: %s %s' % (self.cl_conf['name'], self.service))
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
            params[param] = self.cl_conf[param]
      
        scan_dict['params'] = params
 
        self.scan_db.append(scan_dict)
     
   
    def get_accuracy(self):
        return self.scan_db

        #acc_sort = sorted(self.scan_db, key=lambda x:-x['sort'])

        #for acc in acc_sort:
        #    message = 'acc (normal)=%s, acc (anomaly)=%s : ' % (acc['acc1'], acc['acc0'])

            #for param in const.MLPARAMS:
            #    message += ' %s=%s' % (param, acc['params'][param])           

        #    logger.info(message)
        #    logger.info(pformat(acc))


    def diff_anomaly(self):
        db = Sqlite3Helper(self.db_conf)
        fields = db.select(where='service="%s"' % self.service,
                           base_match=self.cl_conf)
        db.close()


        center = {}
        distance = const.INVALID

        for field in fields:
            feature = field['feature']

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

        db = Sqlite3Helper(self.db_conf)
        db.update_many(update, where, buffers)
