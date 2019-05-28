from logging import getLogger

logger = getLogger(__name__)

import math
import pickle
import difflib
import numpy as np

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


    def clustering(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service
            self.model_vec_path = util_path.model_vec_path(self.cl_conf, service)
            self.model_cls_path = util_path.model_cls_path(self.cl_conf, service)

            vector_type = self.cl_conf['vector_type']
            cluster_type = self.cl_conf['cluster_type']

            func = getattr(self, "%s_to_%s" % (vector_type, cluster_type), None)
            if func is not None:
                func()

            else:
                logger.info('%s to %s not supported' % (vector_type, cluster_type))


            if self.cl_conf['use_diff'] == 'True':
                self.diff_anomaly()


    def doc2vec_to_isolationforest(self):
 
        data, tags = util_reader.get_data_from_doc2vec(self.model_vec_path)
        self.cluster_isolationforest(data, tags) 
      

    def fasttext_to_isolationforest(self):
        db = Sqlite3Helper(self.db_conf)
        data, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)
 
        data = util_reader.get_data_from_fasttext(self.model_vec_path, data)
        self.cluster_isolationforest(data, tags) 


    def doc2vec_to_dbscan(self):
 
        data, tags = util_reader.get_data_from_doc2vec(self.model_vec_path)
        self.cluster_dbscan(data, tags) 


    def fasttext_to_dbscan(self): 
        db = Sqlite3Helper(self.db_conf)
        data, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)

        data = util_reader.get_data_from_fasttext(self.model_vec_path, data)
        self.cluster_dbscan(data, tags) 


    def cluster_isolationforest(self, data, tags):
        data = np.array(data)

        cl_conf = self.cl_conf
        model = IsolationForest(behaviour=cl_conf['cluster_behaviour'],
                                n_estimators=int(cl_conf['cluster_n_estimators']),
                                contamination=cl_conf['cluster_contamination'],
                                random_state=int(cl_conf['cluster_random_state']),
                                max_samples=int(cl_conf['cluster_max_samples']))
        model.fit(data)
        pred_data = model.predict(data)

        self.dump_to_db(tags, pred_data, data)          
 
        pickle.dump(model, open(self.model_cls_path, 'wb'))


    def cluster_dbscan(self, data, tags):
        data = np.array(data)

        cl_conf = self.cl_conf
        model = DBSCAN(eps=float(cl_conf['cluster_eps']),
                       min_samples=int(cl_conf['cluster_min_samples']))
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

        db = Sqlite3Helper(self.db_conf)
        db.create_table()

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
        
            update = 'prediction="%s",feature="%s"' % (prediction, 
                                                       label)
            where = 'tag="%s"' % tag 

            db.update(update, where)


    def diff_anomaly(self):
        db = Sqlite3Helper(self.db_conf)
        fields = db.select(where='service="%s"' % self.service,
                           base_match=self.cl_conf)

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

            update = 'diff="%s"' % ('\n'.join(diff))
            where = 'tag="%s"' % field['tag']

            db.update(update, where)

