from logging import getLogger

logger = getLogger(__name__)

import math
import pickle
import numpy as np

from gensim.models.doc2vec import Doc2Vec
from sklearn.ensemble import IsolationForest

from .sqlite3_helper import *
from .util import reader as util_reader
from .const import Const as const

class VectorCluster:

    def __init__(self, conf, index):

        self.conf      = conf
        self.index     = index
        self.db_conf   = conf.db_conf
        self.base_conf = conf.base_confs[index]
        self.tv_conf   = conf.tv_confs[index]
        self.vc_conf   = conf.vc_confs[index]

        self.service = ''
        self.tv_path    = ''
        self.vc_path    = ''

        self.conf = conf


    def initialize(self):

        work_dir = self.conf.work_dir

        if not self.db_conf.path:
            self.db_conf.path = work_dir + '/database.db'

        if not self.tv_conf.dir:
            self.tv_conf.dir = work_dir

        if not self.vc_conf.dir:
                self.vc_conf.dir = work_dir


    def clustering(self):

        for service in self.base_conf.services:
            self.service = service

            model = '%s.%s.vec.model' % (self.base_conf.name,
                                        self.service)
            self.tv_path = self.tv_conf.dir + '/' + model

            model = '%s.%s.cls.model' % (self.base_conf.name,
                                        self.service)
            self.vc_path = self.vc_conf.dir + '/' + model

            if self.tv_conf.type == 'doc2vec':
                if self.vc_conf.type == 'isolationforest':
                    self.doc2vec_to_isolationforest()
                else:
                    logger.info('%s not supported' % (self.vc_conf.type))
            else:
                logger.info('%s not supported' % (self.tv_conf.type))



    def doc2vec_to_isolationforest(self):
        vc_conf = self.vc_conf
 
        data, tags = util_reader.get_data_from_doc2vec(self.tv_path)
        data = np.array(data)
      
        model = IsolationForest(behaviour=vc_conf.behaviour,
                                n_estimators=vc_conf.n_estimators,
                                contamination=vc_conf.contamination,
                                random_state=vc_conf.random_state,
                                max_samples=vc_conf.max_samples)
        model.fit(data)
        pred_data = model.predict(data)

        self.dump_to_db(tags, pred_data, data)          
 
        pickle.dump(model, open(self.vc_path, 'wb'))


    def dump_to_db(self, tags, pred_data, data):
        db = Sqlite3Helper(self.conf, self.index)
        db.create_table()

        labels = []
        means  = []

        for ii, pred in enumerate(pred_data):
            if pred == const.NORMAL:
                means.append(data[ii]) 

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
        
            update = 'prediction="%s",feature="%s"' % (prediction, 
                                                       label)
            where = 'tag="%s"' % tag 

            db.update(update, where)


