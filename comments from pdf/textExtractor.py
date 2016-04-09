import pdfquery
import unicodedata
from pyPdf import PdfFileReader

class txtExtractor:
    def __init__(self,fileName):
        self.pdfQuery = pdfquery.PDFQuery(fileName)
        self.pdf = PdfFileReader(file(fileName,"rb"))
        self.x_off = float(self.pdf.pages[0].trimBox[0])
        self.y_off = float(self.pdf.pages[0].trimBox[1])
        self.lastPage=-1

    def pdf_to_text(self):
        num_of_pages = self.pdfQuery.doc.catalog['Pages'].resolve()['Count']
        res = []
        for i in range(num_of_pages):
            res.append(self.get_text_from_page(i))
        return res

    def get_text_from_page(self,pageNum):
        self.pdfQuery.load(pageNum)
        resDict = self.pdfQuery.extract([#('with_parent','LTPage[pageid="%s"]' % (pageNum)),
                                    ('with_formatter', 'text'),
                                    ('text','LTTextLineHorizontal')])
        unitext = resDict['text']
        if type(unitext) == unicode:
            text = unicodedata.normalize('NFKD', unitext).encode('ascii','ignore')
        else:
            text = unitext
        text = text.replace("- ","")
        text = text.replace("fi ","fi")
        return text

    def get_text_from_box(self,pageNum,coordinatesList):
        return self.__text_pdf__(pageNum,coordinatesList)

    def __text_pdf__(self,pageNum,coordinates):
        if self.lastPage!=pageNum:
            self.pdfQuery.load(pageNum)
            self.lastPage=pageNum
        x=coordinates[0] + self.x_off
        y=coordinates[1] + self.y_off
        w=coordinates[2] + x
        h=coordinates[3] + y
        resDict = self.pdfQuery.extract([
                                    ('with_formatter', 'text'),
                                    ('text','LTTextLineHorizontal:overlaps_bbox("%s,%s,%s,%s")' % (round(x),round(y),round(w),round(h)))])
        unitext = resDict['text']
        if type(unitext) == unicode:
            text = unicodedata.normalize('NFKD', unitext).encode('ascii','ignore')
        else:
            text = unitext
        text = text.replace("- ","")
        text = text.replace("fi ","fi")
        return text
