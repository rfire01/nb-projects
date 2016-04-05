from lxml import etree
import numpy
import string

def create_tree(filepath):
    file=open(filepath,'rb')
    text = file.read()
    file.close()
    printable = set(string.printable)
    xml = filter(lambda x: x in printable, text)
    return etree.fromstring(xml)

def bigger_than(mid,val,epsilon):
    if(val-mid > epsilon):
        return True
    else:
        return False

#parser = etree.XMLParser(recover=True)
#pages = create_tree('ch1sci.xml')
pages=etree.parse('tmp.xml').getroot()
size_list = []

paging=[]
amount =0
size_total=0
last=''

fonts={}


for page in pages:
    single_page=[]
    for text_box in page:
        box=[]
        for text_line in text_box:
            line=""
            min_size=1000000000000

            for text in text_line:
                if 'size' in text.attrib:

                    amount=amount+1
                    size_total=size_total+float(text.attrib['size'])

                    min_size = min(float(text.attrib['size']),min_size)
                    size_list.append(float(text.attrib['size']))
                    #if float(text.attrib['size'])> 14:
                        #a=1
                if type(text.text)==type('') and all(c !='\n' for c in text.text):
                    if 'font' in text.attrib:
                        if not text.attrib['font'] in fonts:
                            fonts[text.attrib['font']]=1
                            last = text.attrib['font']
                        else:
                            fonts[text.attrib['font']]=fonts[text.attrib['font']]+1
                            last = text.attrib['font']
                    line = line + text.text
            if min_size !=  1000000000000:
            #    box.append([line,0,last])
            #else:
                box.append([line,min_size,last])
            line=""
        single_page.append(box)
        box=[]
    paging.append(single_page)
    single_page=[]
                #print text.attrib['size']

try:
    del fonts['']
except KeyError:
    pass

mid =numpy.median(size_list)
#a=1
print mid

size_list=[]

for p in paging:
    for b in p:
        for l in b:
            if l[1]-mid > 0.0001 and l[0]!='':
                size_list.append(l[1])


from collections import Counter
print sorted(Counter(size_list).keys())
large_sizes = Counter(size_list)
length = len(large_sizes)

label_mid = numpy.median(size_list)
print label_mid
print numpy.average(size_list)
size_list.sort()
print size_list

new_mid=numpy.median(large_sizes.keys())
closest = max(large_sizes.keys())
chosen=-1
if not new_mid in large_sizes.keys():
    for key in large_sizes.keys():
        if new_mid-key < closest and new_mid-key>0:
            closest=new_mid-key
            chosen=key
#new_mid=sorted(large_sizes.keys())[-4]

print new_mid


import operator
sorted_fonts = sorted(fonts.items(), key=operator.itemgetter(1))


print ""
print "OUTPUT:"
print ""


##################################################################################################
from numpy import mean, absolute

def mad(data, axis=None):
    return mean(absolute(data - mean(data, axis)), axis)

#for p in paging:
#    for b in p:
#        for l in b:
#            if length<3:
#            #if abs(label_mid-l[1]) < 0.0001 and l[0]!='':
#
#                if bigger_than(mid,l[1],0.0001) and l[0]!='':
##                    if l[1] == 13.824:
#                        a=1
#                    print l[0]
#            else:
#                if new_mid<=l[1] and l[0]!='':
#                    print l[0]

old=0
ind=0
for fon in sorted_fonts:
    if fon[1] > old * 10:
       ind = sorted_fonts.index(fon)-1
    old=fon[1]

label_fonts = []
for fon in sorted_fonts:
    if fon[1]<=sorted_fonts[ind][1] and fon[1]>=sorted_fonts[ind][1]*0.5:
        label_fonts.append(fon[0])

#############################################################################################################
fonts2={}
fonts3={}

for page in pages:
    for text_box in page:
        for text_line in text_box:
            check=False
            for text in text_line:
                if type(text.text)==type('') and all(c !='\n' for c in text.text):
                    if 'font' in text.attrib and 'size' in text.attrib:
                        if float(text.attrib['size'])-mid>0.0001:
                            if not text.attrib['font'] in fonts2:
                                fonts2[text.attrib['font']]=1
                            else:
                                fonts2[text.attrib['font']]=fonts2[text.attrib['font']]+1
                            check=True
                            last=text.attrib['font']
            if check:
                if not last in fonts3:
                    fonts3[last]=1
                else:
                    fonts3[last]=fonts3[last]+1

vals=fonts2.values()
mid_fonts=numpy.average(vals)
sorted_fonts2 = sorted(fonts2.items(), key=operator.itemgetter(1))
sorted_fonts3 = sorted(fonts3.items(), key=operator.itemgetter(1))


both=[]
ma=mad(vals)
for f in sorted_fonts2:
    if f[0] in label_fonts and (f[1]<=mid_fonts+ma and f[1]>=mid_fonts-ma):
        both.append(f[0])
#############################################################################################################



for p in paging:
    for b in p:
        for l in b:
            if bigger_than(mid,l[1],0.0001) and l[0]!='' and l[2] in both:
                print l[0]