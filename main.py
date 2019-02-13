#import pdfkit
#import weasyprint
import requests
from os import mkdir
import os.path
from bs4 import BeautifulSoup
import json
#import urllib
import traceback
import sys
#import shutil
from time import sleep
import re

class Ripper:

    def __init__(self, weburl):
        self.weburl = weburl
        self.soup = None
    
    def print_trace(self):
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
    
    def clean_str(self,str_):
        str_ = str_.strip()
        str_ = re.sub(r'[^\x00-\x7F]+', '', str_)
        str_ = re.sub(r'[:\'\"?%><|]+', '', str_)
        return str_

    def connect(self, url):
        connection = False
        while connection == False:
            try:
                #print("10 seconds cooldown")
                #sleep(10)
                #headers = {'User-Agent': 'Mozilla/5.0'}
                print ("connecting to", url)
                page = requests.get(url, timeout=300)#, headers=headers)
                if page.status_code == 406:
                    print ("status code 406 raising error")
                    raise requests.exceptions.ConnectionError
                print ("connected successfully to", url, "Status Code:", page.status_code)
                self.soup = BeautifulSoup(page.content, 'html.parser')
                page.close()
                connection = True
                if page.status_code == 404:
                    return False
                else:
                    return True
            except requests.exceptions.ConnectionError:
                print("Connection Refused")
                print("Let me sleep for 5 seconds")
                sleep(5)
                print("Back again")
            except:
                print("Unknown error")
                exit()

    def findWclass(self, item, cls):
        return self.soup.findAll(item , {"class" : lambda x : x and cls in x.split()})

    def createDir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def writePdf(self, link, title):
        #pdf = weasyprint.HTML(link).write_pdf()
        #file(title+'.pdf', 'w').write(pdf)
        if os.path.isfile('./'+title+'.pdf'):
            print('./'+title+'.pdf ' + "Exists. Skipping")
            return None
        connection = False
        local_file = title+'.pdf'
        while connection == False:
            try:
                #print("2 seconds cooldown")
                #sleep(2)
                api_endpoint = 'http://selectpdf.com/api2/convert/'
                key = '56f6e575-a95a-4eb9-b809-7799e99d6e49'
                test_url = link

                # parameters - add here any needed API parameter
                parameters = {
                    'key': key,
                    'url': test_url
                }
                requesturl = api_endpoint #urllib.parse.urlencode(api_endpoint).encode("utf-8")
                print ("Calling {0}\n".format(requesturl))
                request = requests.get(requesturl, params=parameters, timeout=300, headers={'Content-Type':'application/json','User-Agent': 'Mozilla/5.0'})
                print("success")
                localFile = open(local_file, 'wb')
                print("opened", local_file)
                localFile.write(request.content)
                localFile.close()
                request.close()
                print ("Test pdf document generated successfully!")
                connection = True
            except requests.exceptions.ConnectionError:
                print("Connection Refused")
                print("Let me sleep for 5 seconds")
                sleep(5)
                print("Back again")
            except OSError:
                print("OS ERROR... cleaning string")
                local_file = self.clean_str(local_file)
            except:
                self.print_trace()
                exit()

    def scrape(self):
        print("Start of scrape")
        self.createDir("categories")
        self.connect(self.weburl)
        print("Main web connected")
        categories = self.findWclass("li","menu-item-object-category")
        cLinks = [category.find('a', href = True)["href"] for category in categories]
        print ("cLinks:",str(len(cLinks)))
        for cLink in cLinks:
            accum = 1
            print("cLink")
            fldname = ''.join(categories[cLinks.index(cLink)].find('a').contents)
            self.createDir("categories/"+str(fldname))
            while True:
                if not self.connect(cLink+"page/"+str(accum)):
                    break
                print("This is page", accum)
                articles = self.findWclass("h2","entry-title")
                aLinks = [article.find('a', href = True)["href"] for article in articles]
                aTitles = [article.find('a', href = True)["title"] for article in articles]
                print("iterating over articles")
                for aLink, aTitle in zip(aLinks, aTitles): self.writePdf(aLink, "categories/"+str(fldname)+'/'+aTitle) #pdfkit.from_url(aLink, "categories/"+str(fldname)+'/'+aTitle+'.pdf')
                print("Page",accum,"done")
                accum += 1

if __name__ == "__main__":
    print("WEB RIPPER")
    WEBSITE = "https://thisguywrites.com"
    ripper = Ripper(WEBSITE)
    ripper.scrape()
    print("DONE")
