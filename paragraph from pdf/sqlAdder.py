from sqlalchemy import create_engine
import sqlalchemy
import pandas as pd
import unicodedata

class sqlModifier:
    def __init__(self):
        self.engine = create_engine('postgresql://postgres@localhost:5432/nota-bene DB')
        self.engine.execution_options(autocommit=True, autoflush=False, expire_on_commit=False)

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
        self.create_table()
        self.delete_from_marked_table(source_id)
        for subject in subjects.keys():
            query = "INSERT INTO tbl_pdf_subject_text VALUES (%d,%d,%d,%r,%r)" %(source_id,subject[0],subjects[subject][0],subject[1],subjects[subject][1])
            try:
                pd.io.sql.execute(sqlalchemy.text(query), self.engine)
            except:
                print "sql insert failed"

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


