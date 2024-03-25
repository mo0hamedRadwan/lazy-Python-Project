import requests
from bs4 import BeautifulSoup

class UpbamServer():
    def __init__(self):
        self.session = requests.Session()

    def getHeader(self):
        headers = {
            'authority': 'upbam.org',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'cookie': 'lang=english; ref_url=https%3A%2F%2Ftv.cimaaa4u.pics%2F;',
            'origin': 'https://upbam.org',
            'referer': 'https://upbam.org/ci6r1k6jg26l',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        return headers

    def getDownloadLink(self, url):
        self.id = url.split('/')[-1]
        headers = self.getHeader()
        data = {
            'op': 'download2',
            'id': self.id,
            'rand': '',
            'referer': 'https://tv.cimaaa4u.pics/'
        }
        response = self.session.post(url, data=data, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        span = soup.find('span', id="direct_link")
        link = span.a['href']
        print(link)

    def __del__(self):
        self.session.close()

upbam = UpbamServer()
upbam.getDownloadLink('https://upbam.org/ci6r1k6jg26l')