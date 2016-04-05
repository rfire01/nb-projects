instructions for subject_text.py

before starting: 
open sqlAdder.py and change the database name to match the one you use.
(if not working on localhost or port 5432, line 8 in same file also needed to be updated)

1.import:
from subject_text import subject_text

2.creating an instance:
st = subject_text()

3.extracting text by subjects:
#in order to work, the pdf need to be in folder tmp, and its name is "source_id.pdf"
#this function create "tbl_pdf_subject_text" table in your db if not exists, and add the results to the table
#the function returns a dictionary where key = (subject_index,subject), value = [subject_page,body]
##subject index - the order of the subjects in the pdf
##subject - string with the subject
##subject page - the page where the subject starts
##body - the text of the subject

st.get_subjects(source_id)