from logging import getLogger

logger = getLogger(__name__)

import os
import pickle
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#from sklearn.externals import joblib
import joblib

from .sqlite3_helper import *
from .util import reader as util_reader
from .util import path as util_path
from .const import Const as const

import smtplib
from email.mime.text import MIMEText

class AnomalyAlert:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]

        self.service   = ''
        self.model_vec_path   = ''
        self.model_cls_path   = ''
        self.model_scl_path   = ''

        self.plot_path     = ''

        self.predictions = []

        self.conf = conf


    def predict(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service
            self.model_vec_path = util_path.model_vec_path(self.cl_conf, service)
            self.model_cls_path = util_path.model_cls_path(self.cl_conf, service)
            self.model_scl_path = util_path.model_scl_path(self.cl_conf, service)
            self.plot_path = util_path.plot_path(self.cl_conf, service)

            vector_type = self.cl_conf['vector_type']
            vector_func = getattr(self, "get_data_from_%s" % (vector_type), None)
            data, tags = vector_func()

            cluster_type = self.cl_conf['cluster_type']
            cluster_func = getattr(self, "predict_%s" % (cluster_type), None)
            pred_data = cluster_func(data)
            pred_dict = {'service': service,
                         'data': data,
                         'tags': tags,
                         'pred_data': pred_data }

            self.predictions.append(pred_dict)

            buffers = []
            for tag, pred in zip(tags, pred_data):
                buffers.append([str(pred), tag]) 
            
            update = 'prediction=?'
            where = 'tag=?'

            db = Sqlite3Helper(self.db_conf)
            db.update_many(update, where, buffers)
            db.close()


    def plot(self):
        for prediction in self.predictions:
            self.plot_path = util_path.plot_path(self.cl_conf, prediction['service'])
            self.plot_clustering(prediction['data'], 
                                 prediction['tags'], 
                                 prediction['pred_data'])


    def alert(self):
        contents = ''

        for prediction in self.predictions:
            messages = ''

            if self.cl_conf['use_diff'] == 'True':
                messages = self.get_anomaly_diff(prediction['tags'], 
                                 prediction['pred_data'])
                if not messages:
                    continue

            else:
                messages = self.get_anomaly(prediction['tags'], 
                                 prediction['pred_data'])
                if not messages:
                    continue

            contents += '**********************************************************************\n'
            contents += 'cluster ID: %s\n' % self.cl_conf['name']
            contents += 'target hosts: %s\n' % self.cl_conf['hosts']
            contents += 'target service: %s\n' % prediction['service']
            contents += '**********************************************************************\n'
            if self.cl_conf['use_diff'] == 'True':
                contents += '\n'
                contents += 'Differences are shown below.\n'
            else:
                contents += '\n'
                contents += 'Anomaly messages are shown below.\n'
            contents += messages
            contents += '\n\n'

        return contents

 
    def alert_anomaly(self, contents):
        if not contents:
            logger.info('No anomaly events are observed')
            return

        message  = 'This is a test system to detect anomaly events in logwatch outputs\n'
        message += 'using Machine Learning technologies.\n\n'

        message += 'Anomaly events have been detected.\n\n'

        message += contents

        message += '\n'
        message += 'The following hosts and servides are currently monitored:\n\n'

        for name in self.conf['DEFAULT']['clusters'].split(','):
            message += '* %s\n' % self.conf[name]['hosts']

            for service in self.conf[name]['services'].split(','):
                message += ' - %s\n' % service

        if self.conf['alert']['to_address'] == 'dummy':
            print (message)

        else:
            subject = 'Logwatch alert: anomaly events detected'
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From']    = self.conf['alert']['from_address']
            msg['To']      = self.conf['alert']['to_address']

            smtp = smtplib.SMTP()
            smtp.connect()
            smtp.sendmail(self.conf['alert']['from_address'], self.conf['alert']['to_address'], msg.as_string())

            smtp.close()


    def get_anomaly(self, tags, pred_data):
        diff = ''
        db = Sqlite3Helper(self.db_conf)

        counter = 0

        for tag, pred in zip(tags, pred_data):
            if pred != int(const.ABNORMAL):
                continue
             
            counter += 1
          
            if counter > 5:
                continue

            where = 'tag="%s"' % (tag)
            field = db.select(where, self.cl_conf)[0]
        
            diff += '======================================================================\n'            
            diff += field['date'] + ' ' + field['host']
            diff += field['data'] 
            diff += '\n\n'
            diff += '======================================================================\n'            

        if counter > 5:
            diff += 'There are other %s events.' % (counter - 5)
            diff += '\n\n'

        return diff


    def get_anomaly_diff(self, tags, pred_data):
        diff = ''
        db = Sqlite3Helper(self.db_conf)

        counter = 0

        for tag, pred in zip(tags, pred_data):
            if pred != int(const.ABNORMAL):
                continue
             
            counter += 1
          
            if counter > 3:
                continue

            where = 'tag="%s"' % (tag)
            field = db.select(where, self.cl_conf)[0]
        
            if not field['diff']:
                continue

            diff += '======================================================================\n'            
            diff += field['diff'] 
            diff += '\n\n'
            diff += '======================================================================\n'            


        if counter > 3:
            diff += 'There are other %s events.' % (counter - 3)
            diff += '\n\n'

        return diff


    def get_data_from_doc2vec(self):
        db = Sqlite3Helper(self.db_conf)
        docs, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)

        data = util_reader.get_data_from_doc2vec(self.model_vec_path, docs, self.cl_conf)

        if self.cl_conf['cluster_normalize'] == 'True':
            mm = joblib.load(self.model_scl_path)
            data = mm.transform(data).tolist()

        return data, tags


    def get_data_from_fasttext(self):

        db = Sqlite3Helper(self.db_conf)
        docs, tags = util_reader.get_data_from_sqlite3(db,
                                                      'service="%s"' % self.service,
                                                       self.cl_conf)

        data = util_reader.get_data_from_fasttext(self.model_vec_path, docs, self.cl_conf)

        if self.cl_conf['cluster_normalize'] == 'True':
            mm = joblib.load(self.model_scl_path)
            data = mm.transform(data).tolist()

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
        if conf['cluster_count_int'] == 'True':
            vector_dim -= 1
        if conf['cluster_count_word'] == 'True':
            vector_dim -= 1

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
                    if (ix+1) > (vector_dim + arbitrary_dim + 1):
                        label = 'Word count'
                    elif (ix+1) > (vector_dim + arbitrary_dim):
                        label = 'Int count'
                    elif (ix+1) > vector_dim:
                        label = 'Arbitrary %s' % (ix-vector_dim)
                    axes[iy][ix].set_xlabel(label)
                if (ix == (0)):
                    label = 'Feature %s' % iy
                    if (iy+1) > (vector_dim + arbitrary_dim + 1):
                        label = 'Word count'
                    elif (iy+1) > (vector_dim + arbitrary_dim):
                        label = 'Int count'
                    elif (iy+1) > vector_dim:
                        label = 'Arbitrary %s' % (iy-vector_dim)
                    axes[iy][ix].set_ylabel(label)

        fig.legend([a,b], ['normal events', 'anomaly events'])
        plt.savefig(self.plot_path)
