instructions for autoDownload.py

before starting:
make sure you have in the same folder of autoDownload.py "tmp" and "downloads" folders

1.import:
from autoDownload import downloader

2.creating an instance:
d = downloader()

3.downloading files:
#in the end of the process all pdfs will be in tmp folder with the source id as their name

d.download_pdfs(list of source ids)

REQUIREMENTS:

-selenium
-chromedriver (can be downloaded from https://sites.google.com/a/chromium.org/chromedriver/downloads)