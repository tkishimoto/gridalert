from logging import getLogger

logger = getLogger(__name__)

from .logwatch_template import *

class LogwatchfineTemplate(LogwatchTemplate):

    def __init__(self, conf):
        super().__init__(conf)


    def initialize(self):
        for service in self.conf['cl']['services'].split(','):                  
 
            if ('dmlite' in service): 
                if ('dmlite' in self.service_names):
                    continue

                self.service_keys.append(['- dmlite Begin -', 
                                          '- dmlite End -'])
                self.service_names.append('dmlite')

            elif (service == 'login-sshd'):
                self.service_keys.append(['- SSHD Begin -',
                                          '- SSHD End -'])
                self.service_names.append('sshd')

            else:
                logger.info('%s not supported' % (service))
           

    def execute(self, text):

        buffers = []
        buffers_tmp = []
        logwatch = False

        for line in  open(text, errors='replace'):
      
            if ('##### Logwatch' in line) and (not 'End' in line):
                logwatch = True

            if logwatch:
                buffers_tmp.append(line)

            if ('##### Logwatch End' in line):
                logwatch = False
                buffers += self.extract(buffers_tmp)
                buffers_tmp = []

        return buffers


    def extract(self, lines):
        # shoud return lists of 'cluster', 'host', 'date',
        #              'service', 'metadata', 'data', 'label'  

        buffers = []
        meta = {}
        unix = ''
        for ii, key  in enumerate(self.metadata_keys):
            data = 'unknown'

            for line in lines:
                data = util_text.extract_sline(line, key[0], key[1])

                if data:
                    if 'date' in self.metadata_names[ii]:
                        unix = util_date.endate_to_unix(data)
                        data = util_date.endate_to_sqdate(data)
                    
                    break

            meta[self.metadata_names[ii]] = data

        for ii, key  in enumerate(self.service_keys):
            data = util_text.extract_mline(lines, key[0], key[1])
            if data == '':
                data = 'unknown'
                continue 

            # cluster, host, date, service, metadata, data, label
            service  = self.service_names[ii]

            if service == 'dmlite':
                buffers += self.dmlite(meta, data)

            if service == 'sshd':
                buffers += self.sshd(meta, data)

        return buffers


    def dmlite(self, meta, data):
        buffers = []
        service = 'dmlite'

        lines = data.split('\n')
        for line in lines:

            if line.replace(' ', '').replace('\n', '') == '':
                continue

            # host, date, service, metadata, data, label
            host     = meta['host']
            date     = meta['date']
            metadata = 'range=%s,level=%s' % (meta['range'], meta['level'])
            label    = '1'
            buffers.append([host, date, service,
                            metadata, line, label])
        return buffers


    def sshd(self, meta, data):
        buffers = []
        service = 'login-sshd'

        lines = data.split('\n')

        header = ''
        login = ''
        login_buffer = []

        for line in lines:
            if 'Users logging in through sshd:' in line:
                header = '\n' + line + '\n'
                continue
            
            elif '' == header:
                header = ''
                continue

            if not header:
                continue

            if line[0:4] == '    ' and line[4] != ' ': 
                if login == '':
                    login += line + '\n'
                else:
                    login_buffer.append(header + login)
                    login = line + '\n'

            if login != '' and line[0:7] == '       ' and line[7] != ' ':
                login += line + '\n'

        login_buffer.append(header + login)

        for login in login_buffer:
            # host, date, service, metadata, data, label
            host     = meta['host']
            date     = meta['date']
            metadata = 'range=%s,level=%s' % (meta['range'], meta['level'])
            label    = '1'

            buffers.append([host, date, service,
                            metadata, login, label])
        return buffers

        

