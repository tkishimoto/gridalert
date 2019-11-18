from logging import getLogger

logger = getLogger(__name__)

import re

from ..util import date as util_date
from ..util import text as util_text
from ..util import hash as util_hash

from ..elastic_helper import *

class ElasticTemplate:

    def __init__(self, conf):

        self.conf = conf


    def initialize(self):
        return
           

    def execute(self, text):

        buffers = [] 

        query = {}
        if 'logstash-dpm' in text:
            query = {'size'   : 0,
                     '_source': ['data', 'host.name'],
                     'query'  : {'bool': {'minimum_should_match':1, 
                                          'must_not': [{'wildcard':{'data': 'xrootd*', 
                                                                    'data':'*Cached*',
                                                                    'data':'*empty*',
                                                                    'data':'*record*' }},]}}}

            es = ElasticHelper(self.conf)
            scroll = es.get_scroll(query, text)

            messages = {}

            # cluster, host, date, service, metadata, data, label
            for res in scroll:
                host = res['_source']['host']['name']
                break
            date     = '%s 00:00:00' % (text.split('-')[-1].replace('.', '-'))
            service  = '-'.join(text.split('-')[:-1])
            metadata = ''
            label    = '1'
     
            for data in self.aggregate_dpm(messages, scroll):
                buffers.append([host, date, service,
                                metadata, data, label])

        return buffers



    def aggregate_dpm(self, messages, scroll):

        for res in scroll:
            r = res['_source']
            line = r['data']

            process = line.split()[0]
            level = line.split()[1]

            if '!!!' not in level:
                continue

            if 'httpd' in process:
                process = 'httpd'
            elif 'xrootd' in process:
                process = 'xrootd'
            elif 'globus-gridftp-server' in process:
                process = 'globus-gridftp-server'
            else:
                process = 'other'

            data = ' '.join(line.split()[2:])

            data_filter = ''

            for word in data.split():
                 
                if re.match('\'\/dpm\/.*\/home\/.*\'', word):
                    word = 'DPM_LFN'

                if re.match('\/dpm\/.*\/home\/.*', word):
                    word = 'DPM_LFN'

                if re.match('\'\/.*\/\d{4}-\d{2}-\d{2}\/.*\'', word):
                    word = 'DPM_LFN'

                if re.match('\/.*\/\d{4}-\d{2}-\d{2}\/.*', word):
                    word = 'DPM_LFN'

                if '[0x' in word:
                    word = 'HEXNUMBNER'

                if re.match('\'..\'', word):
                    word = 'RAMDOM_DIR'

                if word.isdigit():
                    word = 'NUMBER'

                if re.match('\(\d+\)', word):
                    word = '(NUMBER)'
 
                if re.match('\(\d+', word):
                    word = '(NUMBER'

                if re.match('\d+,', word):
                    word = 'NUMBER,'

                if re.match('id\:\d+', word):
                    word = 'id:NUMBER,'

                if re.match('\d+\)', word):
                    word = 'NUMBER)'

                if re.match('\'\d+\-..\'', word):
                    word = 'FILE_KEY'

                if 'https://dpmhead-rc.cern.ch/' in word:
                    tmp_words = ''
                    for tmp_word in re.split('&t=|&free=|&tot=|\'', word):
                        if tmp_word.isdigit():
                            tmp_words = tmp_words + '&param=NUMBER'
                        else:
                            tmp_words = tmp_words + tmp_word
                    word = tmp_words

                # ATLAS experiment
                if re.match('.*\.root.*', word):
                    word = 'FILE_NAME'

                if re.match('.*\.log\.tgz.*', word):
                    word = 'FILE_NAME'

                if re.match('.*\.pic\.gz.*', word):
                    word = 'FILE_NAME'

                if re.match('\d+\:\'.*\'', word):
                    word = 'FILE_NAME'

                if re.match('(data|user|group|panda|log|NTUP|AOD|DAOD|EVNT|ESD|DESD|HITS|RDO|output|test).*\)\.', word):
                    word = 'FILE_NAME'

                if re.match('\'(data|user|group|panda|log|NTUP|AOD|DAOD|EVNT|ESD|DESD|HITS|RDO|output|test)\..*\'', word):
                    word = 'FILE_NAME'

                if re.match('.*(data|user|group|panda|log|NTUP|AOD|DAOD|EVNT|ESD|DESD|HITS|RDO|output|test)\..*\.root\..*', word):
                    word = 'FILE_NAME'

                if re.match('.*testfile.*ATLAS.*', word):
                    word = 'FILE_NAME'

                if re.match('.*storagesummary.*', word):
                    word = 'FILE_NAME'

                if re.match('.*GridFTP\-Probe\-argo\-mon.*', word):
                    word = 'FILE_NAME'

                if re.match('.*tar\.gz*', word):
                    word = 'FILE_NAME'

                if re.match('.*physics\_Main\.merge*', word):
                    word = 'FILE_NAME'


                # ICEPP
                word = re.sub(r'data\d\d', 'dataXX', word)
                word = re.sub(r'lcg\-fs\d\d\d', 'lcg-fsXXX', word)
                word = re.sub(r'20\d\d\-\d\d\-\d\d', '20XX-XX-XX', word)

                data_filter = data_filter + ' ' + word

            data_filter = process + ' : ' + data_filter
            if data_filter in messages.keys():
                messages[data_filter] += 1
            else:
                messages[data_filter] = 1

        results = []

        messages_sorted = sorted(messages.items(),
                                 key=lambda x:-x[1])
        for data in messages_sorted:
            count = str(data[1]).rjust(8)
            message = data[0]
            results.append('%s time(s) : %s\n' % (count, message))  

        return results
    
