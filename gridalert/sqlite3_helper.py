from logging import getLogger

logger = getLogger(__name__)

import sqlite3

from .util import match as util_match

class Sqlite3Helper:

    def __init__(self, conf, index=-1):
        self.conf = conf
        self.db_conf = conf.db_conf
        self.base_conf = conf.base_confs[index]

        self.conn = sqlite3.connect(self.db_conf.path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()


    
    def create_data_table(self):
        db_conf = self.db_conf
        self.create_table(db_conf.data_table_name,
                     db_conf.data_column_names,
                     db_conf.data_column_types)

    def create_grid_table(self):
        db_conf = self.db_conf
        self.create_table(db_conf.grid_table_name,
                     db_conf.grid_column_names,
                     db_conf.grid_column_types)


    def create_table(self, table_name, column_names, column_types):
        create = []

        for ii, name in enumerate(column_names):
            create.append('%s %s' % (name, column_types[ii]))

        create = ','.join(create)

        create = 'create table if not exists %s (%s)' % (table_name, create)
        self.cur.execute(create)
        self.conn.commit()


    def insert_data_many(self, data):
        db_conf = self.db_conf
        self.insert_many(db_conf.data_table_name,
                         db_conf.data_column_names,
                         data)


    def insert_many(self, table_name, column_names, data):
        questions = ','.join(['?' for ii in column_names])
        insert = '%s' % ','.join(column_names)
        insert = 'insert or ignore into %s (%s) values (%s)' % (table_name,
                                                      insert,
                                                      questions)
        self.cur.executemany(insert, data)
        self.conn.commit()


    def select_data_where(self, where):
        db_conf = self.db_conf
        base_conf = self.base_conf
        fields = self.select_where(db_conf.data_table_name,
                             db_conf.data_column_names,
                             where)

        results = []
        for field in fields:
            if util_match.base_match(base_conf, field['host'], field['date']):
                results.append(field)

        return results


    def select_data_service(self, service):
        db_conf = self.db_conf
        base_conf = self.base_conf
        fields = self.select(db_conf.data_table_name,
                             db_conf.data_column_names)
         
        results = []
        for field in fields:
            if not field['service'] == service:
                continue

            if not util_match.base_match(base_conf, field['host'], field['date']):
                continue

            results.append(field)
           
        return results


    def select_grid_service(self, service):
        db_conf = self.db_conf
        base_conf = self.base_conf

        fields_grid = self.select(db_conf.grid_table_name,
                             db_conf.grid_column_names)
        results = []
        for field in fields_grid:
            tag = field['tag']
            where = 'tag="%s"' % tag
            data = self.select_data_where(where)[0]
     
            if not data['service'] == service:
                continue  
  
            if not util_match.base_match(base_conf, data['host'], data['date']):
                continue

            results.append(field)

        return results


    def select_where(self, table_name, column_names, where):
        select = ','.join(column_names)
        select = 'select %s from %s ' % (select, table_name)

        select += 'where %s' % where
        select += ' order by tag'

        self.cur.execute(select)
        return self.cur.fetchall()


    def select(self, table_name, column_names):
        select = ','.join(column_names)
        select = 'select %s from %s ' % (select, table_name)

        if self.db_conf.select_where:
            select += 'where %s' % self.db_conf.select_where

        select += ' order by tag'
        print (select)
        self.cur.execute(select)
        return self.cur.fetchall()


    def replace_grid_many(self, data):
        db_conf = self.db_conf
        self.replace_many(db_conf.grid_table_name,
                         db_conf.grid_column_names,
                         data)


    def replace_many(self, table_name, column_names, data):
        questions = ','.join(['?' for ii in column_names])
        insert = '%s' % ','.join(column_names)
        insert = 'replace into %s (%s) values (%s)' % (table_name,
                                                      insert,
                                                      questions)
        self.cur.executemany(insert, data)
        self.conn.commit()


    def update_grid(self, update, where):
        update = 'update %s set %s where %s' % (self.db_conf.grid_table_name, update, where)
        self.cur.execute(update)
        self.conn.commit()


    def close(self):
        self.conn.commit()
        self.conn.close()
