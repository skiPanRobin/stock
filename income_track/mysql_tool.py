import pymysql
from pymysql.cursors import DictCursor


class MysqlTool:

    def __init__(self, charset='utf8mb4'):
        self.host = '119.91.142.194'
        self.port = 3306
        self.user = 'root'
        self.password = 'mariadb'
        self.db = 'stock_data'
        self.charset = charset
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
    sql = "SELECT date, `code`, `name`, high, low, `open`, closed, pe_dynamic, volume  from " \
          "stock_zh_ah_name WHERE date = DATE_SUB(CURRENT_DATE,INTERVAL 1 DAY) AND `code` = '000002';"
    with mt.cursor as cur:
        cur.execute(sql)
        print(cur.fetchall())
    mt.disconnect()


if __name__ == '__main__':
    demo()
