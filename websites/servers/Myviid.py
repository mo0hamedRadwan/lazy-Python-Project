import requests
from bs4 import BeautifulSoup
import re


class MyviidServer():
    def __init__(self):
        self.session = requests.Session()

    def getDownloadPage(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        tabel = soup.find('table', class_="tbl1")
        if(tabel != None):
            func = tabel.a['onclick']
            parms = re.findall("'(.*?)'", func)
            # Mode(n) => Normal , Mode(h) => High
            link = f"https://myviid.com/dl?op=download_orig&id={parms[0]}&mode={parms[1]}&hash={parms[2]}"
            return link
        print("File Not Found")
        exit()

    def getDownloadLink(self, url):
        page = self.getDownloadPage(url)
        response = self.session.get(page)
        soup = BeautifulSoup(response.text, 'lxml')
        link = soup.find_all('span')[-1].a['href']
        print(link)

    def __del__(self):
        self.session.close()


myviid = MyviidServer()
myviid.getDownloadLink('https://vidhd.best/d/b3u54xfkb6am.html')
