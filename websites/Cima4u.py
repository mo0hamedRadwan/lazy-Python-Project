import requests
from bs4 import BeautifulSoup
from urllib import parse
from websites.UserAgent import userAgent
#from UserAgent import userAgent
import random


class Cima4u():
    def __init__(self, domainName="cimaaa4u.online"):
        self.session = requests.Session()
        self.proxies = self.getProxies()
        self.domainName = domainName
        self.movies = []
        self.seasons = []
        self.episodes = []

    def setUrl(self, url):
        soup = self.makeRequest(url)
        svg = soup.find('div', id="SliderShapeSVGs")
        if(svg == None):
            if(f"tv.{self.domainName}" in url):
                if(soup.title.text == "خطاء 404"):
                    print("setUrl: Page Not Found in mycima")
                    exit()
                self.url = url
                self.soup = self.makeRequest(self.url)
            elif(self.domainName in url):
                SingleContentSide = soup.find(
                    'div', class_="SingleContentSide")
                self.url = SingleContentSide.find_all('a')[2]['href']
                self.soup = self.makeRequest(self.url)
            else:
                print("setUrl: Wrong Domain Name Or URL")
                exit()
        else:
            print("setUrl: Page Not Found in mycima")
            exit()

    def searchBy(self, keywords):
        keywords = parse.quote_plus(keywords)
        url = f'https://{self.domainName}/search/{keywords}'
        soup = self.makeRequest(url)
        blocks = soup.find_all('li', class_="MovieBlock")
        result = []
        for block in blocks:
            link = block.find('a')['href']
            result.append(self.getUrlDetails(link))
        return result

    def getHeader(self):
        headers = {
            'authority': self.domainName,
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': f'https://{self.domainName}',
            'referer': "https://www.google.com",
            'user-agent': random.choice(userAgent),
            'x-requested-with': 'XMLHttpRequest',
        }
        return headers

    def startScraping(self):
        seasons = self.soup.find('div', class_="SeasonsSectionsList")  # Series
        if(seasons != None):
            items = seasons.find_all('a')
            if('/Video/' in self.url):
                self.getMovies(items)
            elif('/Episode/' in self.url):
                self.getSeasons(items)
            else:
                pass
        else:  # movie
            pass

        info = self.getInfo()
        return self.getTableView(info)

    def makeRequest(self, url):
        while True:
            proxy = {'http': random.choice(self.proxies)}
            response = self.session.get(
                url, headers=self.getHeader(), proxies=proxy)
            soup = BeautifulSoup(response.text, 'lxml')
            if((soup.title != None) and (response.status_code == 200)):
                return soup

    def getProxies(self, fileName="./Proxies.txt"):
        try:
            with open(fileName, 'r') as file:
                return [p.rstrip() for p in file]
        except:
            print("getProxies: Proxies FileName Not Found!")
            exit()

    def getMovies(self, items):
        for item in items:
            self.movies.append(item['href'])

    def getSeasons(self, items):
        for item in items:
            self.seasons.append(item['href'])

        for season in self.seasons:
            self.getEpisodes(season)

    def getEpisodes(self, season):
        soup = self.makeRequest(season)
        episodes = soup.find_all('li', class_="EpisodeItem")
        videos = []
        for episode in episodes:
            link = episode.find('a')['href']
            videos.append(link)
        self.episodes.append(videos)

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
        print(soup.prettify())
        link = url
        title = soup.find('div', class_="SingleContent").h1.text
        video = {'title': title, 'image': "",
                 'rating': "", 'notes': '-', 'link': link}
        return video

    def getWatchLinks(self, url):
        soup = self.makeRequest(url)

        serversWatchSide = soup.find('div', class_="serversWatchSide")
        servers = serversWatchSide.find_all('a')
        Links = []
        for server in servers:
            name, id = server.text, server['data-link']
            Links.append({'name': name, 'link': self.getServer(id)})
            # print(name, "=>", id)
        return Links

    def getServer(self, id):
        headers = {
            'authority': f'tv.{self.domainName}',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'origin': f'https://tv.{self.domainName}',
            'referer': self.url,
            'user-agent': random.choice(userAgent),
            'x-requested-with': 'XMLHttpRequest',
        }
        params = {'id': id}
        data = {'id': id}

        proxy = {'http': random.choice(self.proxies)}
        response = requests.post(
            f'https://tv.{self.domainName}/structure/server.php', proxies=proxy,
            params=params, headers=headers, data=data)
        # print(response.text)
        soup = BeautifulSoup(response.text, 'html5lib')
        if(soup.find('iframe') != None):
            link = soup.find('iframe')['src'].replace('\n', '')
            #print(link)
            return link

    def getDownloadLinks(self, url):
        soup = self.makeRequest(url)

        DownloadServers = soup.find('div', class_="DownloadServers")
        servers = DownloadServers.find_all('a')
        links = []
        for server in servers:
            name, link = server.text, server['href']
            links.append({'name': name, 'quality': "", 'link': link})
            # print(name, " => ", link)
        return links

    def clearData(self):
        self.movies.clear()
        self.seasons.clear()
        self.episodes.clear()

    def __del__(self):
        self.session.close()


# cima = Cima4u("cimaaa4u.yachts")
# url = "https://tv.cimaaa4u.yachts/Video/Venus+2022-53734.html"
# cima.setUrl(url)
# cima.startScraping()
