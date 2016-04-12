from sqlalchemy import create_engine
import sqlalchemy
import pandas as pd
import unicodedata
import psycopg2
import select
import psycopg2.extensions as extensions
from psycopg2 import OperationalError

class sqlModifier:
    def __init__(self,dataBaseName):
        self.db = dataBaseName
        self.engine = create_engine('postgresql://postgres@localhost:5432/%s' % (self.db))
        self.engine.execution_options(autocommit=True, autoflush=False, expire_on_commit=False)

    def create_conn(self):
        db = "dbname=%r user=postgres" % (self.db)
        self.conn = psycopg2.connect(db)


    def wait_select(self,conn):
        while 1:
            state = conn.poll()
            if state == extensions.POLL_OK:
                break
            elif state == extensions.POLL_READ:
                select.select([conn.fileno()], [], [])
            elif state == extensions.POLL_WRITE:
                select.select([], [conn.fileno()], [])
            else:
                raise OperationalError("bad state from poll: %s" % state)

    def create_table(self):
        query = ("CREATE TABLE IF NOT EXISTS tbl_pdf_marked_text("
                "location_id integer,"
                "source_id integer,"
                "ensemble_id integer,"
                "page integer,"
                "x integer,"
                "y integer,"
                "w integer,"
                "h integer,"
                "body text,"
                "comment_id integer"
                ")")
        pd.io.sql.execute(sqlalchemy.text(query), self.engine)

    def add_marked_text(self,source_id,comments):
        from contextlib import closing
        self.create_conn()
        self.wait_select(self.conn)
        with closing(self.conn.cursor()) as cursor:
            for comment in comments:
                SQL = "INSERT INTO tbl_pdf_marked_text VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                data = (comments[comment]['location_ID'],source_id,comments[comment]['ensemble_ID'],comments[comment]['page'],comments[comment]['x'],comments[comment]['y'],comments[comment]['w'],comments[comment]['h'],comments[comment]['body'],comment,)
                cursor.execute(SQL, data)
        self.conn.commit()
        self.conn.close()

    def delete_from_marked_table(self,source_id):
        query = "DELETE FROM tbl_pdf_marked_text WHERE source_id=%s" %(source_id)
        pd.io.sql.execute(sqlalchemy.text(query), self.engine)

    def get_comment_id_text(self,comment_id):
        query = "SELECT * FROM tbl_pdf_marked_text WHERE comment_id=%s" %(comment_id)
        df = pd.read_sql_query(sqlalchemy.text(query), con = self.engine)
        body = df.at[0,'body']
        if type(body) == unicode:
            return unicodedata.normalize('NFKD', body).encode('ascii','ignore')
        else:
            return body

    def check_if_exist(self ,source_id):
      query = "select count(id) as cnt from tbl_pdf_marked_text where source_id={0}".format(source_id)
      record_count = pd.read_sql_query(query, con=self.engine).cnt.values[0]
      return record_count> 0