from logging import getLogger

logger = getLogger(__name__)

class HtmlHelper:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]


    def make_html(self):
        print ('test')
