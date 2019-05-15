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
from .sqlite3_helper import *

class DataVisualizer:

    def __init__(self, conf, index):

        self.conf      = conf
        self.index     = index
        self.db_conf   = conf.db_conf
        self.base_conf = conf.base_confs[index]
        self.tv_conf   = conf.tv_confs[index]
        self.vc_conf   = conf.vc_confs[index]
        self.dv_conf   = conf.dv_confs[index]

        self.service  = ''
        self.tv_path    = ''
        self.vc_path    = ''

        self.html_sub_dir = ''
        self.html_path    = ''
        self.html_top_path    = ''
        self.plot_path    = ''

        self.conf = conf


    def initialize(self):

        work_dir = self.conf.work_dir

        if not self.db_conf.path:
            self.db_conf.path = work_dir + '/database.db'

        if not self.tv_conf.dir:
            self.tv_conf.dir = work_dir

        if not self.vc_conf.dir:
            self.vc_conf.dir = work_dir

        if not self.dv_conf.html_dir:
            self.dv_conf.html_dir = work_dir

        if not self.dv_conf.plot_dir:
            self.dv_conf.plot_dir = work_dir

        if not self.html_top_path:
            self.html_top_path = work_dir + '/gridalert.top.html'


    def visualize(self):

        for service in self.base_conf.services:
            self.service = service

            model = '%s.%s.vec.model' % (self.base_conf.name,
                                        self.service)

            self.tv_path = self.tv_conf.dir + '/' + model

            model = '%s.%s.cls.model' % (self.base_conf.name,
                                        self.service)

            self.vc_path = self.vc_conf.dir + '/' + model

            html_sub = '%s.%s.sub.html' % (self.base_conf.name,
                                           self.service)

            self.html_sub_dir = self.dv_conf.html_dir + '/' + html_sub

            plot = '%s.%s.svg' % (self.base_conf.name,
                                           self.service)
            
            self.plot_path = self.dv_conf.plot_dir + '/' + plot

            html = '%s.%s.html' % (self.base_conf.name,
                                           self.service)

            self.html_path = self.dv_conf.html_dir + '/' + html

            if self.tv_conf.type == 'doc2vec':
                if self.vc_conf.type == 'isolationforest':
                    self.plot_doc2vec_isolationforest()
                else:
                    logger.info('%s not supported' % (self.vc_conf.type))
            else:
                logger.info('%s not supported' % (self.tv_conf.type))

            if self.dv_conf.use_diff:
                self.diff_anomaly()

            self.make_sub_html()

        self.make_top_html()


    def plot_doc2vec_isolationforest(self):

        data, tags = util_reader.get_data_from_doc2vec(self.tv_path)

        cluster_model = pickle.load(open(self.vc_path, 'rb'))
        pred_data = cluster_model.predict(data)

        self.plot_clustering(data, tags, pred_data)


    def plot_clustering(self, data, tags, pred_data):
        conf = self.conf

        ndim = len(data[0])
        data = np.array(data)

        fig, axes = plt.subplots(nrows=ndim, ncols=ndim)

        for ix in range(ndim):
            for iy in range(ndim):

                xx1  = []
                xx2  = []
                yy1  = []
                yy2  = []
                tag1 = []
                tag2 = []

                for ii, pred in enumerate(pred_data):
                    if pred == 1:
                        xx1.append(data[ii][ix])
                        yy1.append(data[ii][iy])
                        tag1.append('%s/%s.html' % (self.html_sub_dir, tags[ii]))
                    else:
                        xx2.append(data[ii][ix])
                        yy2.append(data[ii][iy])
                        tag2.append('%s/%s.html' % (self.html_sub_dir, tags[ii]))

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
        db = Sqlite3Helper(self.conf, self.index)
        fields_grid = db.select_grid_service(self.service)

        center = {}
        distance = 9999

        for field in fields_grid:
            feature = field['feature']
           
            data = {}
            for index in feature.split(','):
                data[index.split('=')[0]] = index.split('=')[1]

            if float(data['distance']) < distance:
                distance = float(data['distance'])
                center = field

        where = 'tag="%s"' % center['tag']
        center_data = db.select_data_where(where)[0]

        for field in fields_grid:
            where = 'tag="%s"' % field['tag']
            data = db.select_data_where(where)[0]

            diff = difflib.unified_diff(center_data['data'].splitlines(),
              data['data'].splitlines(),
              'normal event',
              'anomaly event',
              '%s %s %s' % (center_data['host'], self.service, center_data['date']),
              '%s %s %s' % (data['host'], self.service, data['date']))

            update = 'diff="%s"' % ('\n'.join(diff))
            where = 'tag="%s"' % field['tag']

            db.update_grid(update, where)


    def make_sub_html(self):
        
        db   = Sqlite3Helper(self.conf, self.index)
        fields = db.select_grid_service(self.service)
 
        if not os.path.exists(self.html_sub_dir):
            os.makedirs(self.html_sub_dir)

        html = open(self.html_path, 'w')
        self.html_header(html)
        html.write('<h4>gridalert clustering visualization</h4>\n')
        html.write('<ul>\n')
        html.write('<li>host machines = %s</li>\n' % (','.join(self.base_conf.hosts)))
        html.write('<li>service = %s</li>\n' % (self.service))
        html.write('<li>vecter algorithm = %s</li>\n' % (self.tv_conf.type))
        html.write('<li>clustering algorithm = %s</li>\n' % (self.vc_conf.type))
        html.write('</ul>\n')

        html.write('<object type="image/svg+xml" data="%s"></object>' % self.plot_path)
        html.write('<h4>link to orignal logs</h4>\n')
        html.write('<ul>\n')
        for field in fields:
            where = 'tag="%s"' % field['tag']
            data = db.select_data_where(where)[0]

            if field['prediction'] == '1':
                html.write('<li><a href="%s/%s.html">%s %s %s</a></li>\n' % (self.html_sub_dir, 
                                                                             data['tag'], 
                                                                             data['host'], 
                                                                             data['service'], 
                                                                             data['date']))
            else:
                html.write('<li><a href="%s/%s.html">%s %s %s (anomaly)</a></li>\n' % (self.html_sub_dir, 
                                                                                       data['tag'], 
                                                                                       data['host'], 
                                                                                       data['service'], 
                                                                                       data['date']))
        html.write('</ul>\n')
        self.html_footer(html)
        html.close()

        for field in fields:
            where = 'tag="%s"' % field['tag']
            data = db.select_data_where(where)[0]
            html = open('%s/%s.html' % (self.html_sub_dir, data['tag']), 'w')
            self.html_header(html)
            html.write('<h4>original logs</h4>\n')
            html.write('<ul>\n')
            html.write('<li>host machine = %s</li>\n' % (data['host']))
            html.write('<li>service = %s</li>\n' % (data['service']))
            html.write('<li>date = %s</li>\n' % (data['date']))
            html.write('</ul>\n')
            html.write('%s' % data['data'].replace('\n', '<br>'))
            html.write('<h4>diff to normal log</h4>\n')
            html.write('%s' % field['diff'].replace('\n', '<br>'))
            self.html_footer(html)
            html.close()

         
    def make_top_html(self):

        html = open(self.html_top_path, 'w')
        self.html_header(html)
        html.write('<h4>gridalert top page</h4>\n')
        html.write('<ul>\n')
        for name in self.conf.get_base_names():
            html.write('<li>%s</li>\n' % name) 
            html.write('<ul>\n')
            for service in self.base_conf.services:
                html.write('<li><a href="./%s.%s.html">%s</a></li>\n' % (name, service, service)) 
            html.write('</ul>\n')

        html.write('</ul>\n')
        self.html_footer(html)
        html.close()


    def html_header(self, html):
        html.write('<!DOCTYPE html>\n')
        html.write('<html>\n')
        html.write('<head>\n')
        html.write('<title>gridalert monitor</title>\n')
        html.write('<meta charset="UTF-8">\n')
        html.write('</head>\n')
        html.write('<body>\n')

    def html_footer(self, html):
        html.write('</body>\n')
        html.write('</html>\n')
 


 


