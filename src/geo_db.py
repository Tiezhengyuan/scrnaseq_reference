import os
import sqlite3

class GeoDb:
    def __init__(self, indir:str, db_name):
        self.db = os.path.join(indir, f'{db_name}.db')

    def drop_table(self, table_name:str):
        try:
            conn = sqlite3.connect(self.db)
            sql = f"DROP TABLE {table_name}"
            conn.execute(sql)
            conn.close()
            # print(f"Drop the new table {table_name}")
        except Exception as e:
            pass

    def create_table(self, sql:str, table_name:str):
        try:
            conn = sqlite3.connect(self.db)
            conn.execute(sql)
            conn.close()
            print(f"Create a new table {table_name}")
        except Exception as e:
            print(f"Failed in creating the table: error={e}")

    def create_table_geo(self):
        '''
        table geo
        '''
        sql = '''
            CREATE TABLE geo (
                sample_id   VARCHAR2(20) PRIMARY KEY,
                geo         VARCHAR2(20) NOT NULL
            );
            '''
        self.create_table(sql, 'geo')

    def create_table_sample(self):
        '''
        table sample
        '''
        sql = '''
            CREATE TABLE sample (
                sample_id   VARCHAR2(20) PRIMARY KEY,
                disease     VARCHAR2(100),
                tissue      VARCHAR2(50),
                cell_type   VARCHAR2(50),
                cell_line   VARCHAR2(50),
                treated     VARCHAR2(50),
                cultivation VARCHAR2(50)
            );
        '''
        self.create_table(sql, 'sample')

    def create_table_rawdata(self):
        '''
        table data
        '''
        sql = '''
            CREATE TABLE rawdata (
                sample_id   VARCHAR2(20) PRIMARY KEY,
                srr         VARCHAR2(100),
                url         VARCHAR2(200)
            );
        '''
        self.create_table(sql, 'rawdata')
    
    def load(self, sql_pool:list):
        m=n=0
        conn = sqlite3.connect(self.db)
        for sql in sql_pool:
            try:
                conn.execute(sql)
                n += 1
            except Exception as e:
                print(e)
                m += 1
        print(f"{n} are inserted. {m} failed.")
        conn.close()

    def count_rows(self, table_name:str):
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            sql = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(sql)
            res = conn.fetchone()
            conn.close()
            return res
        except Exception as e:
            pass