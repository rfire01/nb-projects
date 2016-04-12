from sqlalchemy import create_engine
import sqlalchemy
import pandas as pd
import unicodedata
import psycopg2
import select
import psycopg2.extensions as extensions
from psycopg2 import OperationalError


class sqlModifier:
    def __init__(self):
        self.engine = create_engine('postgresql://postgres@localhost:5432/nota-bene DB')
        self.engine.execution_options(autocommit=True, autoflush=False, expire_on_commit=False)
        self.db = 'nota-bene DB'

    def create_conn(self):
        db = "dbname=%r user=postgres" % (self.db)
        self.conn = psycopg2.connect(db)

    def wait_select(self, conn):
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
        query = ("CREATE TABLE IF NOT EXISTS tbl_pdf_subject_text("
                "source_id integer,"
                "subject_index integer,"
                "subject_page integer,"
                "subject text,"
                "body text"
                ")")
        pd.io.sql.execute(sqlalchemy.text(query), self.engine)

    def add_text_by_subjects(self,source_id,subjects):
        from contextlib import closing
        self.create_table()
        self.delete_from_marked_table(source_id)
        self.create_conn()
        self.wait_select(self.conn)
        with closing(self.conn.cursor()) as cursor:
            for subject in subjects.keys():
                SQL = "INSERT INTO tbl_pdf_subject_text VALUES (%s,%s,%s,%s,%s)"
                data = (source_id,subject[0],subjects[subject][0],repr(subject[1]),repr(subjects[subject][1]))
                cursor.execute(SQL, data)

        self.conn.commit()
        self.conn.close()

    def delete_from_marked_table(self,source_id):
        query = "DELETE FROM tbl_pdf_subject_text WHERE source_id=%s" %(source_id)
        pd.io.sql.execute(sqlalchemy.text(query), self.engine)

    def get_pdf_subjects(self,source_id):
        query = "SELECT * FROM tbl_pdf_subject_text WHERE source_id=%s" %(source_id)
        df = pd.read_sql_query(sqlalchemy.text(query), con = self.engine)
        subjects = df['subject']
        pages = df['subject_page']
        index = df['subject_index']
        body = df['body']
        dict = {}
        for i,subject in enumerate(subjects):
            if type(body[i]) == unicode:
                body_tmp = unicodedata.normalize('NFKD', body[i]).encode('ascii', 'ignore')
            else:
                body_tmp = body[i]
            if type(subject) == unicode:
                sub_tmp = unicodedata.normalize('NFKD', subject).encode('ascii', 'ignore')
            else:
                sub_tmp = subject
            dict[(index[i],sub_tmp)]=[pages[i],body_tmp]
        return dict


