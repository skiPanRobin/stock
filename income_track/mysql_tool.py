import os

import pymysql
from pymysql.cursors import DictCursor


class MysqlTool:
    host = os.getenv('R_MYSQL_HOST') if os.getenv('R_MYSQL_HOST') else 'localhost'
    port = int(os.getenv('R_MYSQL_PORT')) if os.getenv('R_MYSQL_HOST') else 3306
    user = os.getenv('R_MYSQL_USER') if os.getenv('R_MYSQL_USER') else 'root'
    password = os.getenv("R_MYSQL_PW") if os.getenv("R_MYSQL_PW") else 'root'
    # _db = os.getenv('R_MYSQL_DB') if os.getenv('R_MYSQL_DB') else 'stock_income_track'
    db = 'stock_income_track'
    charset = os.getenv('R_MYSQL_CHARSET') if os.getenv('R_MYSQL_CHARSET') else 'utf8mb4'
    uri = os.getenv('R_MYSQL_URI') if os.getenv('R_MYSQL_URI') else '...'

    def __init__(self):
        self.connection, self.cursor = self.connect()

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=DictCursor
            )
            self.cursor = self.connection.cursor
            return self.connection, self.cursor()
        except Exception as e:
            print(f"Failed to connect to MySQL database: {e}")

    def disconnect(self):
        try:
            if self.connection is not None:
                self.connection.close()
                self.connection = None
            if self.cursor is not None:
                self.cursor.close()
                self.cursor = None
        except Exception as e:
            print(f"Failed to disconnect from MySQL database: {e}")

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Failed to execute query: {e}")
            return None

    def execute_update(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            print(f"Failed to execute update: {e}")
            return None


def demo():
    mt = MysqlTool()
    # sql = "SELECT `date`, `code`, `name`, high, low, `open`, closed, pe_dynamic, volume  from " \
    #       "stock_zh_ah_name WHERE date = DATE_SUB(CURRENT_DATE,INTERVAL 1 DAY) AND `code` = '000002';"
    sql = "SELECT code, 1, name, quo, quote_change, ups_downs, volume, turnover, amplitude, high, low, open, closed"
    with mt.cursor as cur:
        cur.execute(sql)
        print(cur.fetchall())
    mt.disconnect()


if __name__ == '__main__':
    demo()
