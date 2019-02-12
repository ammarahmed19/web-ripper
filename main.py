#import pdfkit
#import weasyprint
import requests
from os import mkdir
import os.path
from bs4 import BeautifulSoup
import json
import urllib
import traceback
import sys
import shutil

class Ripper:

    def __init__(self, weburl):
        self.weburl = weburl
        self.soup = None

    def connect(self, url):
        print ("connecting to", url)
        page = requests.get(url, timeout=300)
        print ("connected successfully to", url)
        self.soup = BeautifulSoup(page.content, 'html.parser')
        if page.status_code == 404:
            return False
        else:
            return True

    def findWclass(self, item, cls):
        return self.soup.findAll(item , {"class" : lambda x : x and cls in x.split()})

    def createDir(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    def writePdf(self, link, title):
        #pdf = weasyprint.HTML(link).write_pdf()
        #file(title+'.pdf', 'w').write(pdf)
        api_endpoint = 'http://selectpdf.com/api2/convert/'
        key = '56f6e575-a95a-4eb9-b809-7799e99d6e49'
        test_url = link
        local_file = title+'.pdf'

        # parameters - add here any needed API parameter
        parameters = {
            'key': key,
            'url': test_url
        }
        requesturl = api_endpoint #urllib.parse.urlencode(api_endpoint).encode("utf-8")
        print ("Calling {0}\n".format(requesturl))
        request = requests.get(requesturl, params=parameters, timeout=300, headers={'Content-Type':'application/json'})
        print("success")
        localFile = open(local_file, 'wb')
        print("opened", local_file)
        localFile.write(request.content)
        localFile.close()
        print ("Test pdf document generated successfully!")

    def scrape(self):
        self.createDir("categories")
        self.connect(self.weburl)
        categories = self.findWclass("li","menu-item-object-category")
        cLinks = [category.find('a', href = True)["href"] for category in categories]
        accum = 1
        for cLink in cLinks:
            fldname = ''.join(categories[cLinks.index(cLink)].find('a').contents)
            self.createDir("categories/"+str(fldname))
            while self.connect(cLink+"page/"+str(accum)) == True:
                articles = self.findWclass("h2","entry-title")
                aLinks = [article.find('a', href = True)["href"] for article in articles]
                aTitles = [article.find('a', href = True)["title"] for article in articles]
                for aLink, aTitle in zip(aLinks, aTitles): self.writePdf(aLink, "categories/"+str(fldname)+'/'+aTitle) #pdfkit.from_url(aLink, "categories/"+str(fldname)+'/'+aTitle+'.pdf')
                accum += 1

if __name__ == "__main__":
    print("WEB RIPPER")
    WEBSITE = "https://thisguywrites.com"
    ripper = Ripper(WEBSITE)
    ripper.scrape()
    print("DONE")
