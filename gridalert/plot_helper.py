from logging import getLogger

logger = getLogger(__name__)

import os
import pickle
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .sqlite3_helper import *
from .util import reader as util_reader
from .util import path as util_path
from .const import Const as const

class PlotHelper:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]

        self.service   = ''
        self.model_vec_path   = ''
        self.model_cls_path   = ''

        self.plot_path     = ''

        self.conf = conf


    def plot(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service
            self.model_vec_path = util_path.model_vec_path(self.cl_conf, service)
            self.model_cls_path = util_path.model_cls_path(self.cl_conf, service)
            self.plot_path = util_path.plot_path(self.cl_conf, service)

            vector_type = self.cl_conf['vector_type']
            vector_func = getattr(self, "get_data_from_%s" % (vector_type), None)
            data, tags = vector_func()

            cluster_type = self.cl_conf['cluster_type']
            cluster_func = getattr(self, "predict_%s" % (cluster_type), None)
            pred_data = cluster_func(data)
   
            self.plot_clustering(data, tags, pred_data)


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

    def predict_isolationforest(self, data):

        cluster_model = pickle.load(open(self.model_cls_path, 'rb'))
        pred_data = cluster_model.predict(data)

        return pred_data


    def predict_dbscan(self, data):

        cluster_model = pickle.load(open(self.model_cls_path, 'rb'))
        pred_data = cluster_model.labels_

        return pred_data


    def plot_clustering(self, data, tags, pred_data):
        conf = self.cl_conf

        ndim = len(data[0])
        arbitrary_words = conf['cluster_arbitrary_words']
        arbitrary_dim = 0
        if arbitrary_words != '':
            arbitrary_dim = len(arbitrary_words.split(','))
        vector_dim = ndim - arbitrary_dim
        data = np.array(data)

        fig, axes = plt.subplots(nrows=ndim, ncols=ndim)

        for ix in range(ndim):
            for iy in range(ndim):

                xx1, xx2  = [], []
                yy1, yy2  = [], []
                tag1, tag2 = [], []

                for ii, pred in enumerate(pred_data):
                    if pred != const.ABNORMAL:
                        xx1.append(data[ii][ix])
                        yy1.append(data[ii][iy])
                        tag1.append('http://localhost:8080/log?tag=%s' % tags[ii])
                    else:
                        xx2.append(data[ii][ix])
                        yy2.append(data[ii][iy])
                        tag2.append('http://localhost:8080/log?tag=%s' % tags[ii])

                if (ix == iy):
                    axes[iy][ix].hist([xx1, xx2], 
                                      histtype='barstacked', 
                                      bins=100, 
                                      color=['green', 'red'])

                else:
                    a = axes[iy][ix].scatter(xx1, yy1, s=20, alpha=0.5, 
                                             c='green', edgecolor='k')
                    a.set_urls(tag1)
                    b = axes[iy][ix].scatter(xx2, yy2, s=20, alpha=0.5, 
                                             c='red', edgecolor='k')
                    b.set_urls(tag2)

                if (iy == (ndim-1)):
                    label = 'Feature %s' % ix
                    if (ix+1) > vector_dim:
                        label = 'Arbitrary %s' % (ix-vector_dim)
                    axes[iy][ix].set_xlabel(label)
                if (ix == (0)):
                    label = 'Feature %s' % iy
                    if (iy+1) > vector_dim:
                        label = 'Arbitrary %s' % (iy-vector_dim)
                    axes[iy][ix].set_ylabel(label)

        fig.legend([a,b], ['normal events', 'anomaly events'])
        plt.savefig(self.plot_path)
