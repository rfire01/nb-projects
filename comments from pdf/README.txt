instructions for marked_text_pdf.py

before starting: 
open nbsite/settings_credentials.py and change the database name to match the one you use.
(if not working on localhost or port 5432, sqlAdder.py line 8 also needed to be updated)

1.import:
from marked_text_pdf import markedExtract

2.creating an instance:
m = markedExtract()

3.extracting marked text from pdf using source_id of the pdf:
#in order to work, the pdf need to be in folder tmp, and its name is "source_id.pdf"
#this function create "tbl_pdf_marked_text" table in your db if not exists, and add the results to the table

m.extract_comments_for_pdf(source_id)

4.extracting marked text from pdf by source_id and comment_id:
##if function "extract_comments_for_pdf" already called once or already have the relevant source id in
##"tbl_pdf_marked_text" table, the function can be used.
##if non of the above takes place, function "extract_comments_for_pdf" need to be used first

m.get_text_by_comment_id(comment_id)