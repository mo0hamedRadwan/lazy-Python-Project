import requests
from bs4 import BeautifulSoup
from urllib import parse
from websites.UserAgent import userAgent
#from UserAgent import userAgent
import random
import re


class Shahid4u():
    def __init__(self, domainName="shahed4u.rest"):
        self.session = requests.Session()
        self.proxies = self.getProxies()
        self.domainName = domainName
        self.movies = []
        self.seasons = []
        self.episodes = []

    def setUrl(self, url):
        if(self.domainName in url):
            self.soup = self.makeRequest(url)
            error404 = self.soup.find('div', class_="error404")
            if(error404 != None or len(url) <= 22):  # Wrong Page
                print("getOriginalURL: Page Not Found in shahed4u")
                exit()
            else:
                self.url = url
        else:
            print("getOriginalURL: Wrong Domain Name Or URL")
            exit()

    def searchBy(self, keywords):
        keywords = parse.quote_plus(keywords)
        url = f'https://{self.domainName}/?s={keywords}'
        soup = self.makeRequest(url)
        blocks = soup.find_all('div', class_="content-box")
        result = []
        for block in blocks:
            item = block.find('a')
            link = item['href']
            result.append(self.getUrlDetails(link))
        return result

    def startScraping(self):
        assemblies = self.soup.find('div', id="assemblies")  # Series of Movies
        # Seasons of Series
        seasons = self.soup.find('div', id="seasons")

        if(assemblies != None):
            self.getMovies(assemblies)
        elif(seasons != None):
            self.getSeasons(seasons)
        elif('/assemblies/' in self.url):
            assemblies = self.soup.find('div', class_="MediaGrid")
            self.getMovies(assemblies)
        elif('/series/' in self.url):
            self.getEpisodes(self.url)
        else:  # Movie
            self.id = self.getID()
        info = self.getInfo()
        return self.getTableView(info)

    def getProxies(self, fileName="./Proxies.txt"):
        try:
            with open(fileName, 'r') as file:
                return [p.rstrip() for p in file]
        except:
            print("getProxies: Proxies FileName Not Found!")
            exit()

    def getID(self, url):
        soup = self.makeRequest(url)
        shortlink = soup.find('div', class_="shortlink")
        try:
            link = shortlink.find_all('span')[1].text
            try:
                id = link.split('p=')[1]
            except:
                id = link.split('gt=')[1]
            return id
        except:
            print("Error in Get Id")
            return 0

    def makeRequest(self, url):
        while True:
            proxy = {'http': random.choice(self.proxies)}
            response = self.session.get(
                url, headers=self.getHeader(url), proxies=proxy)
            soup = BeautifulSoup(response.text, 'lxml')
            if((soup.title != None) and (response.status_code == 200)):
                return soup

    def getMovies(self, assemblies):
        media_blocks = assemblies.find_all('div', class_="media-block")
        # print(len(media_blocks))
        for media in media_blocks:
            link = media.find('a')['href']
            self.movies.append(link)
        self.movies.reverse()

    def getSeasons(self, seasons):
        media_blocks = seasons.find_all('div', class_="media-block")
        for media in media_blocks:
            link = media.find('a')['href']
            self.seasons.append(link)
        self.seasons.reverse()
        for season in self.seasons:
            self.getEpisodes(season)

    def getEpisodes(self, season):
        soup = self.makeRequest(season)
        episodes_list = soup.find('div', id="episodes")
        episodes_block = episodes_list.find_all(
            'div', class_="episode-block")
        videos = []
        for block in episodes_block:
            link = block.find('a')['href']
            videos.append(link)
        videos.reverse()
        # print(len(videos))
        self.episodes.append(videos)

    def getHeader(self, url):
        headers = {
            'authority': self.domainName,
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': f'https://{self.domainName}',
            'referer': (url or (f'https://{self.domainName}')),
            'user-agent': random.choice(userAgent),
            'x-requested-with': 'XMLHttpRequest',
        }
        return headers

    def getInfo(self):
        result = {}
        if(len(self.movies)):  # Series of Movies
            result['type'] = "movieseries"
            result['movieseries'] = self.movies
        elif(len(self.episodes)):  # Series of Episodes
            result['type'] = "series"
            result['series'] = self.episodes
        else:   # Normal Movie
            result['type'] = "movie"
            result['movie'] = [self.url]
        return result

    def getTableView(self, info):
        url_type = info['type']
        url_links = info[url_type]
        links_details = []
        if(url_type == 'series'):
            for i, season in enumerate(url_links):
                for j, episode in enumerate(season):
                    details = self.getUrlDetails(episode)
                    details['notes'] = f'S{i+1}E{j+1}'
                    # print(details)
                    links_details.append(details)
        else:
            for i, url in enumerate(url_links):
                details = self.getUrlDetails(url)
                details['notes'] = f'P{i+1}'
                # print(details)
                links_details.append(details)
        return links_details

    def getUrlDetails(self, url):
        soup = self.makeRequest(url)
        link = url
        img_elem = soup.find('a', class_="poster-image")['style']
        img_src = re.findall("\((.*?)\)", img_elem)[0]
        title = soup.find('div', class_="title").text.strip()
        try:
            imdbR = soup.find('div', class_="imdbR").find('span').text
        except:
            imdbR = ""
        video = {'title': title, 'image': img_src,
                 'rating': imdbR, 'notes': '-', 'link': link}
        return video

    def getWatchLinks(self, url):
        soup = self.makeRequest(url + '/watch')
        servers_list = soup.find('ul', class_="servers-list")
        servers_items = servers_list.find_all('li')
        links = []
        for item in servers_items:
            name = item.text.replace('\n', '')
            self.id = self.getID(url)
            data = {'id': self.id, 'i': item['data-i']}

            headers = self.getHeader(url + '/watch')
            proxy = {'http': random.choice(self.proxies)}
            response = requests.post(
                f'https://{self.domainName}/wp-content/themes/Shahid4u-WP_HOME/Ajaxat/Single/Server.php',
                headers=headers, data=data, proxies=proxy, cookies=self.cookies)
            soup2 = BeautifulSoup(response.text, 'lxml')
            link = soup2.find('iframe')['src']
            #print(f"{name} => {link}")
            links.append({'name': name, 'link': link})
        return links

    def getDownloadLinks(self, url):
        headers = self.getHeader(url + '/download')
        self.id = self.getID(url)
        data = {'id': self.id}

        proxy = {'http': random.choice(self.proxies)}
        response = requests.post(
            f'https://{self.domainName}/wp-content/themes/Shahid4u-WP_HOME/Ajaxat/Single/Download.php',
            headers=headers, data=data, proxies=proxy)
        self.cookies = response.cookies
        soup = BeautifulSoup(response.text, 'lxml')
        download_media = soup.find('div', class_="download-media")
        download_links = download_media.find_all('a')
        links = []
        for d_link in download_links:
            link = d_link['href']
            name = d_link.find('span', class_="name").text
            quality = d_link.find('span', class_="quality").text
            #print(f"{name} => {link}")
            links.append({'name': name, 'quality': quality, 'link': link})
        return links

    def clearData(self):
        self.movies.clear()
        self.seasons.clear()
        self.episodes.clear()

    def __del__(self):
        self.session.close()


# shahid = Shahid4u("shahed4u.hair")
# shahid.getWatchLinks('https://shahed4u.hair/%d9%81%d9%8a%d9%84%d9%85-mission-impossible-fallout-2018-%d9%85%d8%aa%d8%b1%d8%ac%d9%85-3/')