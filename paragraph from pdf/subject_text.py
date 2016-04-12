from lxml import etree
import numpy
from numpy import mean, absolute
import string
import os
import operator
from sqlAdder import sqlModifier
import re

class subject_text:

    def __init__(self):
        self.sm  = sqlModifier()

    def __escape_xml_illegal_chars__(self,val, replacement=''):
        illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')

        return illegal_xml_chars_RE.sub(replacement, val)

    def __create_tree__(self,filepath):
        file=open(filepath,'rb')
        text = file.read()
        file.close()
        printable = set(string.printable)
        xml = filter(lambda x: x in printable, text)
        xml2 = self.__escape_xml_illegal_chars__(xml)
        return etree.fromstring(xml2)

    def __pdf_to_xml_tree__(self,source_id):
        filepath = "tmp/%s.pdf" % (source_id)
        if os.path.isfile(filepath)==False:
            raise Exception('file %s doesnt exists' % (filepath))
        command="python pdf2txt.py -o tmp/tmp_file.xml %s" % filepath
        check_enc = os.system(command)
        if check_enc!=0:
            raise Exception('file %s isnt extractable (file encrypted)' % (filepath))
        return self.__create_tree__('tmp/tmp_file.xml')

    def __first_evaluation__(self,pages):
        size_list = []

        paging = []
        amount = 0
        size_total = 0
        last = ''

        fonts = {}

        for page in pages:
            single_page = []
            for text_box in page:
                box = []
                for text_line in text_box:
                    line = ""
                    min_size = 1000000000000

                    for text in text_line:
                        if 'size' in text.attrib:
                            amount = amount + 1
                            size_total = size_total + float(text.attrib['size'])

                            min_size = min(float(text.attrib['size']), min_size)
                            size_list.append(float(text.attrib['size']))
                        if type(text.text) == type('') and all(c != '\n' for c in text.text):
                            if 'font' in text.attrib:
                                if not text.attrib['font'] in fonts:
                                    fonts[text.attrib['font']] = 1
                                    last = text.attrib['font']
                                else:
                                    fonts[text.attrib['font']] = fonts[text.attrib['font']] + 1
                                    last = text.attrib['font']
                            line = line + text.text
                    if min_size != 1000000000000:
                        box.append([line, min_size, last])
                single_page.append(box)
            paging.append(single_page)

        try:
            del fonts['']
        except KeyError:
            pass

        def check_empty(list):
            res=True
            for item in list:
                if not res:
                    return res
                if type(item)==type([]):
                    res = res and check_empty(item)
                else:
                    return False
            return res
        if check_empty(paging):
            raise Exception('no text found in file:')

        return paging, fonts , numpy.median(size_list)

    def __get_label_fonts__(self,pages,fonts,mid):
        sorted_fonts = sorted(fonts.items(), key=operator.itemgetter(1))

        def mad(data, axis=None):
            return mean(absolute(data - mean(data, axis)), axis)

        old = 0
        ind = 0
        for fon in sorted_fonts:
            if fon[1] > old * 10:
                ind = sorted_fonts.index(fon) - 1
            old = fon[1]

        allowed_fonts = []
        for fon in sorted_fonts:
            if fon[1] <= sorted_fonts[ind][1] and fon[1] >= sorted_fonts[ind][1] * 0.5:
                allowed_fonts.append(fon[0])

        fonts2 = {}

        for page in pages:
            for text_box in page:
                for text_line in text_box:
                    for text in text_line:
                        if type(text.text) == type('') and all(c != '\n' for c in text.text):
                            if 'font' in text.attrib and 'size' in text.attrib:
                                if float(text.attrib['size']) - mid > 0.0001:
                                    if not text.attrib['font'] in fonts2:
                                        fonts2[text.attrib['font']] = 1
                                    else:
                                        fonts2[text.attrib['font']] = fonts2[text.attrib['font']] + 1

        vals = fonts2.values()
        mid_fonts = numpy.average(vals)
        sorted_fonts2 = sorted(fonts2.items(), key=operator.itemgetter(1))

        both = []
        ma = mad(vals)
        for f in sorted_fonts2:
            if f[0] in allowed_fonts and (f[1] <= mid_fonts + ma and f[1] >= mid_fonts - ma):
                both.append(f[0])

        return both

    def __minimal_check__(self,text):
        return any(c.isalpha() for c in text) and len(text)>2

    def process_file(self,source_id,allow_fonts=True):
        try:
            pages = self.__pdf_to_xml_tree__(source_id)
        except Exception as err:
           print "received error in parsing"
           print err.args[0]
           return {}
        #pages = etree.parse('tmp.xml').getroot()

        try:
            paging, fonts, mid = self.__first_evaluation__(pages)
        except Exception as err:
            print "%s %s" % (err.args[0],source_id)
            return {}

        if allow_fonts:
            label_fonts = self.__get_label_fonts__(pages,fonts,mid)

        def bigger_than(mid,val,epsilon):
            if(val-mid > epsilon):
                return True
            else:
                return False

        res={}
        subject=""
        text=""
        subject_index=0
        subject_page=1

        for p in paging:
            for b in p:
                for l in b:
                    if bigger_than(mid,l[1],0.0001) and l[0]!='' and self.__minimal_check__(l[0]):
                        if (allow_fonts==True and l[2] in label_fonts) or allow_fonts==False:
                            if subject=='':
                                res[(subject_index,"prologue (no subject yet)")]=[subject_page,text]
                            else:
                                res[(subject_index,subject)]= [subject_page,text]
                            subject=l[0]
                            subject_page = paging.index(p)+1
                            text=""
                            subject_index = subject_index + 1
                    elif l[0]!='':
                        text = text + " " + l[0]
        res[(subject_index, subject)] = [subject_page, text]

        self.sm.add_text_by_subjects(source_id,res)

        return res

    def get_subjects(self,source_id):
        dict = self.sm.get_pdf_subjects(source_id)
        if dict == {}:
            return self.process_file(source_id)
        else:
            return dict