from logging import getLogger

logger = getLogger(__name__)

import cherrypy

from .sqlite3_helper import *
from .util import html as util_html

class DataVisualizer:

    def __init__(self, conf):

        self.conf       = conf
        self.db_conf    = conf['db']


    @cherrypy.expose
    def index(self):

        html  = util_html.header()
        html += '<h4>gridalert top page</h4>'

        clusters = self.conf['DEFAULT']['clusters'].split(',') 

        html += '<ul>'
        for cluster in clusters:
            html += '<li>%s</li>' % self.conf[cluster]['name']
            html += '<ul>'

            services = self.conf[cluster]['services'].split(',')

            for service in services:
                href = "./service?cluster=%s&service=%s" % (cluster, service)
                html += '<li><a href="%s">%s</a></li>' % (href, service)
            html += '</ul>'
        html += '</ul>'
        html += util_html.footer()
 
        return html


    @cherrypy.expose
    def service(self, cluster, service):

        cl_conf = self.conf[cluster]
        db   = Sqlite3Helper(self.db_conf)
        where = 'service="%s" and prediction=="-1"' % service
        fields = db.select(where=where, base_match=cl_conf)

        prefix = '%s.%s' % (cl_conf['name'], service)
        plot = '%s.svg' % (prefix)

        html  = util_html.header()
        html += '<h4>gridalert clustering visualization</h4>'
        html += '<ul>'
        html += '<li>host machines = %s</li>' % (cl_conf['hosts'])
        html += '<li>text type = %s</li>' % (cl_conf['text_type'])
        html += '<li>service = %s</li>' % (service)
        html += '<li>vecter algorithm = %s</li>' % (cl_conf['vector_type'])
        html += '<li>clustering algorithm = %s</li>' % (cl_conf['cluster_type'])
        html += '</ul>'
        html += '<object type="image/svg+xml" data="/static/%s"></object>' % plot
        html += '<h4>link to anomaly logs</h4>'

        html += '<ul>'
        for field in fields:
            href =  '<li><a href="/log?tag=%s">' % field['tag']
            href += '%s %s' % (field['host'], field['date']) 
            href += '</a></li>' 
            html += href
        html += '</ul>'
        html += util_html.footer()
 
        return html


    @cherrypy.expose
    def log(self, tag):
        db   = Sqlite3Helper(self.db_conf)
        where = 'tag=="%s"' % tag
        field = db.select(where=where)[0]

        html  = util_html.header()
        html += '<h4>original logs</h4>'
        html += '<ul>'
        html += '<li>host machine = %s</li>' % (field['host'])
        html += '<li>service = %s</li>' % (field['service'])
        html += '<li>date = %s</li>' % (field['date'])
        html += '</ul>'
        html += '%s' % field['data'].replace('\n', '<br>')
        html += '<h4>diff to normal log</h4>'
        html += '%s' % field['diff'].replace('\n', '<br>')
        util_html.footer()

        return html
