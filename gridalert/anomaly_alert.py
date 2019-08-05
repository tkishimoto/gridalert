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

from .algorithm import *

from .sqlite3_helper import *
from .util import reader as util_reader
from .util import path as util_path
from .const import Const as const

import smtplib
from email.mime.text import MIMEText
from sklearn.manifold import TSNE

class AnomalyAlert:

    def __init__(self, conf):

        self.conf = conf

        self.service   = ''
        self.model_paths   = []
        self.plot_paths    = []

        self.predictions = []


    def predict(self):
        conf = self.conf

        for service in conf['cl']['services'].split(','):
            self.service = service
            self.model_paths = util_path.model_paths(conf['cl'], service)
            self.plot_paths = util_path.plot_paths(conf['cl'], service)

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
            pred_data, score_data = cluster_func.predict(data, self.model_paths['cls'])

            pred_dict = {'service': service,
                         'data': data,
                         'tags': tags,
                         'pred_data': pred_data,
                         'score_data': score_data }

            self.predictions.append(pred_dict)

            buffers = []
            for tag, pred in zip(tags, pred_data):
                buffers.append([str(pred), tag]) 
            
            update = 'prediction=?'
            where = 'tag=?'

            db = Sqlite3Helper(conf)
            db.update_many(update, where, buffers)
            db.close()


    def plot(self):
        for prediction in self.predictions:
            self.plot_paths = util_path.plot_paths(self.conf['cl'], prediction['service'])
            self.plot_clustering(prediction['data'], 
                                 prediction['tags'], 
                                 prediction['pred_data'])


    def alert(self):
        conf = self.conf
        contents = ''

        for prediction in self.predictions:
            messages = ''

            list_sort = zip(prediction['score_data'],
                            prediction['tags'],
                            prediction['pred_data'])
            list_sorted = sorted(list_sort)
            score_data, tags, pred_data = zip(*list_sorted)


            if conf['cl']['use_diff'] == 'True':
                messages = self.get_anomaly_diff(tags, pred_data, score_data)
                if not messages:
                    continue

            else:
                messages = self.get_anomaly(tags, pred_data, score_data)
                if not messages:
                    continue

            contents += '**********************************************************************\n'
            contents += 'cluster ID: %s\n' % conf['cl']['name']
            contents += 'target hosts: %s\n' % conf['cl']['hosts']
            contents += 'target service: %s\n' % prediction['service']
            contents += '**********************************************************************\n'
            if conf['cl']['use_diff'] == 'True':
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

        for name in self.conf['clusters']:
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


    def get_anomaly(self, tags, pred_data, score_data):
        conf = self.conf
        diff = ''
        db = Sqlite3Helper(conf)

        counter = 0

        for tag, pred, score in zip(tags, pred_data, score_data):
            if pred != int(const.ABNORMAL):
                continue
             
            counter += 1
          
            if counter > 5:
                continue

            where = 'tag="%s"' % (tag)
            field = db.select(where, conf['cl'])[0]
        
            diff += '======================================================================\n'            
            diff += field['date'] + ' ' + field['host'] + ' (score=%s)\n' % round(score, 6)
            diff += field['data'] 
            diff += '\n\n'
            diff += '======================================================================\n'            

        if counter > 5:
            diff += 'There are other %s events.' % (counter - 5)
            diff += '\n\n'

        return diff


    def get_anomaly_diff(self, tags, pred_data, score_data):
        conf = self.conf
        diff = ''
        db = Sqlite3Helper(conf)

        counter = 0

        for tag, pred in zip(tags, pred_data):
            if pred != int(const.ABNORMAL):
                continue
             
            counter += 1
          
            if counter > 3:
                continue

            where = 'tag="%s"' % (tag)
            field = db.select(where, conf['cl'])[0]
        
            if not field['diff']:
                continue

            diff += '======================================================================\n'            
            diff += '(score=%s)\n' % round(score, 6)
            diff += field['diff'] 
            diff += '\n\n'
            diff += '======================================================================\n'            


        if counter > 3:
            diff += 'There are other %s events.' % (counter - 3)
            diff += '\n\n'

        return diff


    def plot_clustering(self, data, tags, pred_data):
        conf = self.conf
        ndim = len(data[0])
        arbitrary_words = conf['cl']['cluster_arbitrary_words']
        arbitrary_dim = 0
        if arbitrary_words != '':
            arbitrary_dim = len(arbitrary_words.split(','))
        vector_dim = ndim - arbitrary_dim
        if conf['cl']['cluster_count_int'] == 'True':
            vector_dim -= 1
        if conf['cl']['cluster_count_word'] == 'True':
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
        plt.savefig(self.plot_paths['cls'])


    def plot_clustering_tsne(self, data, tags, pred_data):
        X_reduced = TSNE(n_components=2, random_state=0).fit_transform(data)
        plt.cla()
        print (X_reduced[:, 0], pred_data)
        plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=pred_data)
        plt.savefig('/root/mnt/test.png')
