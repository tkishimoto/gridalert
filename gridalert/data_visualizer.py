from logging import getLogger

logger = getLogger(__name__)

import os
import pickle
import difflib
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .util import reader as util_reader
from .util import html as util_html
from .const import Const as const
from .sqlite3_helper import *

class DataVisualizer:

    def __init__(self, conf, cluster=const.INVALID):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        
        if not cluster == const.INVALID:
            self.cl_conf    = conf[cluster]

        self.service   = ''
        self.model_vec_path   = ''
        self.model_cls_path   = ''

        self.html_sub_dir  = ''
        self.html_sub_path = ''

        self.plot_path     = ''

        self.conf = conf


    def visualize(self):

        for service in self.cl_conf['services'].split(','):
            self.service = service
            prefix = '%s.%s' % (self.cl_conf['name'], service)

            model = '%s.vec.model' % (prefix)
            self.model_vec_path = self.cl_conf['model_dir'] + '/' + model

            model = '%s.cls.model' % (prefix)
            self.model_cls_path = self.cl_conf['model_dir'] + '/' + model

            html = '%s.html' % (prefix)
            self.html_sub_path = self.cl_conf['html_dir'] + '/' + html

            html_dir = '%s.sub.html' % (prefix)
            self.html_sub_dir = self.cl_conf['html_dir'] + '/' + html_dir

            plot = '%s.svg' % (prefix)
            self.plot_path = self.cl_conf['plot_dir'] + '/' + plot

            if self.cl_conf['vector_type'] == 'doc2vec':
                if self.cl_conf['cluster_type'] == 'isolationforest':
                    self.plot_doc2vec_isolationforest()
                else:
                    logger.info('%s not supported' % (self.cl_conf['cluster_type']))
            else:
                logger.info('%s not supported' % (self.cl_conf['vector_type']))

            if self.cl_conf['use_diff'] == 'True':
                self.diff_anomaly()

            self.make_sub_html()


    def plot_doc2vec_isolationforest(self):

        data, tags = util_reader.get_data_from_doc2vec(self.model_vec_path)

        cluster_model = pickle.load(open(self.model_cls_path, 'rb'))
        pred_data = cluster_model.predict(data)

        self.plot_clustering(data, tags, pred_data)


    def plot_clustering(self, data, tags, pred_data):
        conf = self.conf

        ndim = len(data[0])
        data = np.array(data)

        fig, axes = plt.subplots(nrows=ndim, ncols=ndim)

        for ix in range(ndim):
            for iy in range(ndim):

                xx1, xx2  = [], []
                yy1, yy2  = [], []
                tag1, tag2 = [], []

                for ii, pred in enumerate(pred_data):
                    if pred == const.NORMAL:
                        xx1.append(data[ii][ix])
                        yy1.append(data[ii][iy])
                        tag1.append('%s/%s.html' % (self.html_sub_dir, 
                                                    tags[ii]))
                    else:
                        xx2.append(data[ii][ix])
                        yy2.append(data[ii][iy])
                        tag2.append('%s/%s.html' % (self.html_sub_dir, 
                                                    tags[ii]))

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
                    axes[iy][ix].set_xlabel('Feature %s' % ix)
                if (ix == (0)):
                    axes[iy][ix].set_ylabel('Feature %s' % iy)

        fig.legend([a,b], ['normal events', 'anomaly events'])
        plt.savefig(self.plot_path)


    def diff_anomaly(self):
        db = Sqlite3Helper(self.db_conf)
        fields = db.select(where='service="%s"' % self.service)

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


    def make_sub_html(self):
        
        db   = Sqlite3Helper(self.db_conf)
        fields = db.select(where='service="%s"' % self.service)
 
        if not os.path.exists(self.html_sub_dir):
            os.makedirs(self.html_sub_dir)

        html = open(self.html_sub_path, 'w')
        util_html.header(html)
        html.write('<h4>gridalert clustering visualization</h4>\n')
        html.write('<ul>\n')
        html.write('<li>host machines = %s</li>\n' % (self.cl_conf['hosts']))
        html.write('<li>service = %s</li>\n' % (self.service))
        html.write('<li>vecter algorithm = %s</li>\n' % (self.cl_conf['vector_type']))
        html.write('<li>clustering algorithm = %s</li>\n' % (self.cl_conf['cluster_type']))
        html.write('</ul>\n')

        html.write('<object type="image/svg+xml" data="%s"></object>' % self.plot_path)
        html.write('<h4>link to orignal logs</h4>\n')
        html.write('<ul>\n')
        for field in fields:
            if field['prediction'] == '1':
                html.write('<li><a href="%s/%s.html">%s %s %s</a></li>\n' % (self.html_sub_dir, 
                                                                             field['tag'], 
                                                                             field['host'], 
                                                                             field['service'], 
                                                                             field['date']))
            else:
                html.write('<li><a href="%s/%s.html">%s %s %s (anomaly)</a></li>\n' % (self.html_sub_dir, 
                                                                                       field['tag'], 
                                                                                       field['host'], 
                                                                                       field['service'], 
                                                                                       field['date']))
        html.write('</ul>\n')
        util_html.footer(html)
        html.close()

        for field in fields:
            html = open('%s/%s.html' % (self.html_sub_dir, field['tag']), 'w')
            util_html.header(html)
            html.write('<h4>original logs</h4>\n')
            html.write('<ul>\n')
            html.write('<li>host machine = %s</li>\n' % (field['host']))
            html.write('<li>service = %s</li>\n' % (field['service']))
            html.write('<li>date = %s</li>\n' % (field['date']))
            html.write('</ul>\n')
            html.write('%s' % field['data'].replace('\n', '<br>'))
            html.write('<h4>diff to normal log</h4>\n')
            html.write('%s' % field['diff'].replace('\n', '<br>'))
            util_html.footer(html)
            html.close()

         
    def make_top_html(self):

        html = open(self.conf['DEFAULT']['html_dir'] + '/gridalert.top.html', 'w')
        util_html.header(html)
        html.write('<h4>gridalert top page</h4>\n')
        html.write('<ul>\n')
 
        for name in self.conf['DEFAULT']['clusters'].split(','):
            html.write('<li>%s</li>\n' % self.conf[name]['name']) 
            html.write('<ul>\n')
            for service in self.conf[name]['services'].split(','):
                html.write('<li><a href="./%s.%s.html">%s</a></li>\n' % (self.conf[name]['name'], 
                                                                         service, service)) 
            html.write('</ul>\n')

        html.write('</ul>\n')
        util_html.footer(html)
        html.close()
