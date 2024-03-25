import requests
from bs4 import BeautifulSoup
import re


class LetsUpload():
    def __init__(self):
        self.session = requests.Session()

    def getDownloadLink(self, url):
        url_list = url.split('/')
        new_url = f'https://letsupload.io/video/embed/{url_list[-2]}/1496x616/{url_list[-1]}'
        response = requests.get(new_url)
        soup = BeautifulSoup(response.text, 'lxml')
        video = soup.find('ul', id="playlist1").li
        video_source = video['data-video-source']
        parms = re.findall("'(.*?)'", video_source)
        link = parms[0]
        print(link)
        return link

    def __del__(self):
        self.session.close()


lets = LetsUpload()
lets.getDownloadLink(
    'https://letsupload.io/3h3y2/Shahid4U.Com.Shotgun.Wedding.2022.720p.WEB-DL.mp4')
