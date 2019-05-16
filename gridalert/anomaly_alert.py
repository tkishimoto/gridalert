from logging import getLogger

logger = getLogger(__name__)

import glob
import smtplib
import difflib
from email.mime.text import MIMEText

from .const import Const as const

from .sqlite3_helper import *

class AnomalyAlert:

    def __init__(self, conf):
        self.conf      = conf
        self.db_conf   = conf['db']
        self.aa_conf   = conf['alert']

        self.conf = conf


    def send_mail(self):
        db = Sqlite3Helper(self.db_conf)

        where = 'prediction="%s"' % (const.ABNORMAL)
        if not self.aa_conf['sql_filter'] == 'all':
            where += ' and %s' % self.aa_conf['sql_filter']

        fields = db.select(where)

        contents = ''
        for field in fields:
            if field['diff']:
                contents += field['diff'] 

        if not contents:
            logger.info('No anomaly events are detected')
            return 

        subject = 'Logwatch alert: anomaly events detected' 

        message  = 'This is a test system to detect anomaly events in logwatch outputs\n'
        message += 'using Machine Learning technologies.\n\n'

        message += 'Anomaly events have been detected. Differences are:\n\n'

        message += contents

        message += '\n\n'
        message += 'The following hosts and servides are currently monitored:\n\n'

        clusters = []

        for cluster in self.conf.sections():
            if 'cluster/' in cluster:
                clusters.append(cluster)

        for name in clusters: 
            message += '* %s\n' % self.conf[name]['name']

            for service in self.conf[name]['services'].split(','):
                message += ' - %s\n' % service


        print (message)

        #msg = MIMEText(message)
        #msg['Subject'] = subject
        #msg['From']    = self.conf.alt_from_address
        #msg['To']      = self.conf.alt_to_address

        #smtp = smtplib.SMTP()
        #smtp.connect()
        #smtp.sendmail(self.conf.alt_from_address, [self.conf.alt_to_address], msg.as_string())

        #smtp.close()
