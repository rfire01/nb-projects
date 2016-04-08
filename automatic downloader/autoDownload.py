import os
import time
from os import listdir
from os.path import isfile, join

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui


class downloader:
    def __init__(self):
        def page_is_loaded(driver):
            return driver.find_element_by_tag_name("body") is not None

        def login_success(driver):
            return driver.find_element_by_id("login-name") is not None

        self.download_path = os.path.dirname(os.path.abspath(__file__)) + "\\downloads"
        self.finished_path = os.path.dirname(os.path.abspath(__file__)) + "\\tmp"
        self.options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": self.download_path}
        self.options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=self.options)

        self.driver.get("http://nb.mit.edu:8082/login")

        wait = ui.WebDriverWait(self.driver, 10)
        wait.until(page_is_loaded)
        email_field = self.driver.find_element_by_id("login_user_email")
        email_field.send_keys("admin")
        password_field = self.driver.find_element_by_id("login_user_password")
        password_field.send_keys("nb0721R")
        password_field.send_keys(Keys.RETURN)
        wait = ui.WebDriverWait(self.driver, 10)
        wait.until(login_success)
        # raw_input("press enter after login finished")

    def download_pdfs(self, source_id_list):
        files = dict()
        name_index={}
        handled=[]
        os.chdir(self.download_path)
        # Download loop
        for source in source_id_list:
            succeed = False
            while not succeed:
                try:
                    tmp = self.driver.get("nb.mit.edu:8082/pdf/repository/%s" % source)
                    time.sleep(2)

                    folder_files = filter(os.path.isfile, os.listdir(self.download_path))
                    folder_files = [os.path.join(self.download_path, f) for f in folder_files if
                                    ('.pdf' in f and os.path.join(self.download_path, f).split('.pdf')[0] not in handled)]  # add path to each file

                    folder_files.sort(key=lambda x: os.path.getctime(x))
                    newest_file = folder_files[-1]
                    handled.append(newest_file.split('.pdf')[0])
                    name_index[newest_file.split('.pdf')[0]]=len(name_index)
                    downloaded_files = [f[:f.rfind('.pdf')] for f in listdir(self.download_path) if
                                        isfile(join(self.download_path, f))]

                    # No file downloaded
                    if len(downloaded_files) == len(files):
                        continue

                    succeed=True
                except:
                    pass

        # Wait for files to download.
        while True:
            downloaded_files = [f.split('.')[-1] == 'pdf' for f in listdir(self.download_path) if
                                isfile(join(self.download_path, f))]
            if all(downloaded_files):
                break
            time.sleep(1)

        folder_files = filter(os.path.isfile, os.listdir(self.download_path))
        folder_files_path = [os.path.join(self.download_path, f) for f in folder_files]
        for i,file in enumerate(folder_files_path):
            name = file.split('.pdf')[0]
            if name in name_index:
                files[folder_files[i]] = source_id_list[name_index[name]]

        time.sleep(2)
        # Rename files to source_id.pdf
        for k in files.keys():
            prev = self.download_path + "\\" + str(k)
            next_path = self.finished_path + "\\" + str(files[k]) + ".pdf"
            try:
                os.rename(prev, next_path)
            except:
                print str(files[k])
                continue


        time.sleep(2)