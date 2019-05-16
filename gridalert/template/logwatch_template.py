from logging import getLogger

logger = getLogger(__name__)

from ..util import date as util_date
from ..util import text as util_text

class LogwatchTemplate:

    def __init__(self, cl_conf):

        self.metadata_keys = [] # [[start, end]]
        self.metadata_keys.append(['Logfiles for Host:', '\n'])
        self.metadata_keys.append(['Processing Initiated:', '\n'])
        self.metadata_keys.append(['Date Range Processed:', '\n'])
        self.metadata_keys.append(['Detail Level of Output:', '\n'])

        self.metadata_names = [] 
        self.metadata_names.append('host')
        self.metadata_names.append('date')
        self.metadata_names.append('range')
        self.metadata_names.append('level')

        self.service_keys = [] # [[start, end]]
        self.service_names = [] 

        self.cl_conf = cl_conf


    def initialize(self):
        for service in self.cl_conf['services'].split(','):                  
 
            if (service == 'cron'): 
                self.service_keys.append(['- Cron Begin -', 
                                          '- Cron End -'])
                self.service_names.append('cron')

            elif (service == 'fail2ban'):
                self.service_keys.append(['- ail2ban-messages Begin -', 
                                          '- ail2ban-messages End -'])
                self.service_names.append('fail2ban')

            elif (service == 'iptables_firewall'):
                self.service_keys.append(['- iptables firewall Begin -', 
                                          '- iptables firewall End -'])
                self.service_names.append('iptables_firewall')

            elif (service == 'httpd'):
                self.service_keys.append(['- httpd Begin -', 
                                          '- httpd End -'])
                self.service_names.append('httpd')

            elif (service == 'kernel'):
                self.service_keys.append(['- Kernel Begin -', 
                                          '- Kernel End -'])
                self.service_names.append('kernel')
             
            elif (service == 'pam_unix'):
                self.service_keys.append(['- pam_unix Begin -', 
                                          '- pam_unix End -'])
                self.service_names.append('pam_unix')
    
            elif (service == 'postfix'):
                self.service_keys.append(['- Postfix Begin -', 
                                          '- Postfix End -'])
                self.service_names.append('postfix')

            elif (service == 'sendmail'):
                self.service_keys.append(['- sendmail Begin -', 
                                          '- sendmail End -'])
                self.service_names.append('sendmail')

            elif (service == 'sshd'):
                self.service_keys.append(['- SSHD Begin -', 
                                          '- SSHD End -'])
                self.service_names.append('sshd')

            elif (service == 'disk_space'):
                self.service_keys.append(['- Disk Space Begin -', 
                                          '- Disk Space End -'])
                self.service_names.append('disk_space')

            else:
                logger.info('%s not supported' % (service))
           

    def execute(self, lines):
        # shoud return lists of 'tag', 'cluster', 'host', 'date',
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

            # tag, cluster, host, date, service, metadata, data, label
            tag      = '%s_%s_%s_%s' % (self.cl_conf['name'], meta['host'], 
                                        self.service_names[ii], int(unix))
            cluster  = self.cl_conf['name']
            host     = meta['host']
            date     = meta['date']
            service  = self.service_names[ii]
            metadata = 'range=%s,level=%s' % (meta['range'], meta['level'])
            label    = '1'

            buffers.append([tag, cluster, host, date, service, 
                            metadata, data, label])

        return buffers

