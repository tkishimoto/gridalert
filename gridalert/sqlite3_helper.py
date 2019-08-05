from logging import getLogger

logger = getLogger(__name__)

import sqlite3

from .util import match as util_match
from .const import Const as const

class Sqlite3Helper:

    def __init__(self, conf):

        self.table_name = const.DB_TABLE_NAME
        self.column_names = const.DB_COLUMN_NAMES
        self.column_types = const.DB_COLUMN_TYPES

        self.conn = sqlite3.connect(conf['db']['path'], timeout=600)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()


    def create_table(self):
        create = []

        for ii, name in enumerate(self.column_names):
            create.append('%s %s' % (name, self.column_types[ii]))

        create = ','.join(create)

        create = 'create table if not exists %s (%s)' % (self.table_name, 
                                                         create)
        self.cur.execute(create)
        self.conn.commit()


    def insert_many(self, data):
        questions = ','.join(['?' for ii in self.column_names])
        insert = '%s' % ','.join(self.column_names)
        insert = 'insert or ignore into %s (%s) values (%s)' % (self.table_name,
                                                      insert,
                                                      questions)
        self.cur.executemany(insert, data)
        self.conn.commit()


    def select(self, where='', base_match=''):
        select = ','.join(self.column_names)
        select = 'select %s from %s ' % (select, self.table_name)

        if where:
            select += 'where %s' % where

        select += ' order by tag'

        self.cur.execute(select)
        results = self.cur.fetchall()

        if base_match:
            results_match = []

            for result in results:
                if util_match.base_match(base_match,
                                         result['cluster'],
                                         result['host'],
                                         result['date']):
                    results_match.append(result)
            return results_match

        else:
            return results


    def update(self, update, where):
        update = 'update %s set %s where %s' % (self.table_name, 
                                                update, 
                                                where)
        self.cur.execute(update)
        self.conn.commit()


    def update_many(self, update, where, data):
        update = 'update %s set %s where %s' % (self.table_name,
                                                update,
                                                where)
        self.cur.executemany(update, data)
        self.conn.commit()


    def close(self):
        self.conn.commit()
