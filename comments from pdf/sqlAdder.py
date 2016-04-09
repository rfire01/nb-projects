from sqlalchemy import create_engine
import sqlalchemy
import pandas as pd
import unicodedata

class sqlModifier:
    def __init__(self,dataBaseName):
        self.engine = create_engine('postgresql://postgres@localhost:5432/%s' % (dataBaseName))
        self.engine.execution_options(autocommit=True, autoflush=False, expire_on_commit=False)

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
        for comment in comments:
            query = "INSERT INTO tbl_pdf_marked_text VALUES (%d,%d,%d,%d,%d,%d,%d,%d,%r,%d)" %(comments[comment]['location_ID'],source_id,comments[comment]['ensemble_ID'],comments[comment]['page'],comments[comment]['x'],comments[comment]['y'],comments[comment]['w'],comments[comment]['h'],comments[comment]['body'],comment)
            pd.io.sql.execute(sqlalchemy.text(query), self.engine)

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

