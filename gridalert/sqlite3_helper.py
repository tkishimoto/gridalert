from logging import getLogger

logger = getLogger(__name__)

import sqlite3

from .util import match as util_match
from .const import Const as const

class Sqlite3Helper:

    def __init__(self, conf, index=const.INVALID):
        self.conf = conf
        self.db_conf = conf.db_conf
        self.index = index 

        if not index == const.INVALID:
            self.base_conf = conf.base_confs[index]

        self.conn = sqlite3.connect(self.db_conf.path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()


    def create_table(self):
        db_conf = self.db_conf

        create = []

        for ii, name in enumerate(db_conf.column_names):
            create.append('%s %s' % (name, db_conf.column_types[ii]))

        create = ','.join(create)

        create = 'create table if not exists %s (%s)' % (db_conf.table_name, 
                                                         create)
        self.cur.execute(create)
        self.conn.commit()


    def insert_many(self, data):
        db_conf = self.db_conf
        questions = ','.join(['?' for ii in db_conf.column_names])
        insert = '%s' % ','.join(db_conf.column_names)
        insert = 'insert or ignore into %s (%s) values (%s)' % (db_conf.table_name,
                                                      insert,
                                                      questions)
        self.cur.executemany(insert, data)
        self.conn.commit()


    def select(self, where=''):
        db_conf = self.db_conf
        select = ','.join(db_conf.column_names)
        select = 'select %s from %s ' % (select, db_conf.table_name)

        if where:
            select += 'where %s' % where

        select += ' order by tag'

        self.cur.execute(select)
        results = self.cur.fetchall()

        if self.index == const.INVALID:
            return results

        else:
            base_conf = self.base_conf

            results_match = []
            for result in results:
                if util_match.base_match(base_conf, 
                                         result['host'], 
                                         result['date']):
                    results_match.append(result)

            return results_match


    def update(self, update, where):
        update = 'update %s set %s where %s' % (self.db_conf.table_name, 
                                                update, 
                                                where)
        self.cur.execute(update)
        self.conn.commit()

    def close(self):
        self.conn.commit()
