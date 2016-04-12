from processing import jobs
from textExtractor import txtExtractor
from sqlAdder import sqlModifier
from nbsite import settings_credentials

class markedExtract:
    def __init__(self):
        dbName = settings_credentials.DATABASES["default"]["NAME"]
        self.sql  = sqlModifier(dbName)

    def extract_comments_for_pdf(self,source_id):
        comments, page_com = jobs.process_file(source_id)

        size = len(comments)
        done = 0

        ext = txtExtractor("tmp/%s.pdf"% (str(source_id)))

        cordList = []
        idList = []
        extractList = []
        for page in page_com:
            for comment_id in page_com[page]:
                cord = [comments[comment_id]['x'],comments[comment_id]['y'],comments[comment_id]['w'],comments[comment_id]['h']]
                cordList.append(cord)
                idList.append(comment_id)
            extractList.append([int(page),cordList,idList])
            cordList=[]
            idList=[]


        for pageSet in extractList:
            for source,cord in enumerate(pageSet[1]):
                if not('body' in comments[pageSet[2][source]]):
                    if comments[pageSet[2][source]]['parent'] == -1:
                        text = ext.get_text_from_box((pageSet[0]-1),cord)
                        comments[pageSet[2][source]]['body'] = text
                    else:
                        text = self.__get_parent_body__(comments[pageSet[2][source]]['parent'],comments,ext,pageSet[0])
                        comments[pageSet[2][source]]['body'] = text

            done = done + len(pageSet[1])
            print "done %d%% of the comments" % (100 * done / size)

        self.__add_pdf_to_db__(source_id,comments)

        print "done"

    def get_text_by_comment_id(self,comment_id):
        try:
            return self.sql.get_comment_id_text(comment_id)
        except:
            return "fail"

    def __add_pdf_to_db__(self,source_id,comments,delete=True):
        self.sql.create_table()
        if delete:
            self.sql.delete_from_marked_table(source_id)
        self.sql.add_marked_text(source_id,comments)

    def __get_parent_body__(self,parent_id,comments,extractor,page):
        if 'body' in comments[parent_id]:
            return comments[parent_id]['body']
        else:
            if comments[parent_id]['parent'] == -1:
                cord = [comments[parent_id]['x'],comments[parent_id]['y'],comments[parent_id]['w'],comments[parent_id]['h']]
                text = extractor.get_text_from_box((page-1),cord)
                comments[parent_id]['body'] = text
                return text
            else:
                text = self.__get_parent_body__(comments[parent_id]['parent'],comments,extractor,page)
                comments[parent_id]['body'] = text
                return text