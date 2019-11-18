from logging import getLogger

logger = getLogger(__name__)

from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import scan

from .util import date as util_date
from .const import Const as const

class ElasticHelper:

    def __init__(self, conf):

        options = {
          'host':'%s' % conf['cl']['es_host'],
          'port':9200,
        }

        self.es = Elasticsearch([options])
        self.conf = conf


    def get_indices(self):

        results = [] 

        for service in self.conf['cl']['services'].split(','):
            index = '%s-*' % service
            indices = self.es.cat.indices(index=index, h='index').split('\n')
            indices = sorted(indices)
         
            for ii in indices:
                if ii == '':
                    continue

                date = ii.replace('%s-' % service, '')
                date = '%s 00:00:00' % date.replace('.', '-')
                if util_date.in_sqdate(date,
                                       self.conf['cl']['date_start'],
                                       self.conf['cl']['date_end']):

                    results.append(ii)

        return results
