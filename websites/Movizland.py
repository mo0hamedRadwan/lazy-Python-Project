import requests
from bs4 import BeautifulSoup
from urllib import parse
from websites.UserAgent import userAgent
#from UserAgent import userAgent
import random


class MovizLand():
    def __init__(self, domainName="movizland.xyz"):
        self.session = requests.Session()
        self.proxies = self.getProxies()
        self.domainName = domainName
        self.movies = []
        self.seasons = []
        self.episodes = []

    def setUrl(self, url):
        if(self.domainName in url):
            try:
                response = self.session.get(url)
                if(len(response.url) <= 23):
                    print("setUrl: Page Not Found in movizland")
                    exit()
                self.url = url
                self.soup = self.makeRequest(url)
            except:
                print("setUrl: Request Faild")
                exit()
        else:
            print("setUrl: Wrong Domain Name Or URL")
            exit()

    def searchBy(self, keywords):
        keywords = parse.quote_plus(keywords)
        url = f'https://{self.domainName}/?s={keywords}'
        soup = self.makeRequest(url)
        blocks = soup.find_all('div', class_="BlockItem")
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
        if('/movseries/' in self.url):
            section = self.soup.find('div', id="LoadFilter")
            self.getMovies(section)
        elif('/series/' in self.url):
            self.seasons.append(self.url)
            self.getEpisodes(self.url)
        else:
            series_section = self.soup.find('div', class_="SeriesSingle")
            # Series or Movies Series
            if(series_section != None):
                seasons = series_section.find('ul', 'DropdownFilter')
                if(seasons != None):  # Series
                    self.getSeasons(seasons)
                else:  # Series of Movies
                    self.getMovies(series_section)
            else:  # Movie
                pass

        info = self.getInfo()
        return self.getTableView(info)

    def makeRequest(self, url):
        while True:
            proxy = {'http': random.choice(self.proxies)}
            response = self.session.get(
                url, headers=self.getHeader(), proxies=proxy)
            soup = BeautifulSoup(response.text, 'html5lib')
            if((soup.title != None) and (response.status_code == 200)):
                return soup

    def getProxies(self, fileName="./Proxies.txt"):
        try:
            with open(fileName, 'r') as file:
                return [p.rstrip() for p in file]
        except:
            print("getProxies: Proxies FileName Not Found!")
            exit()

    def getMovies(self, section):
        blocks = section.find_all('div', class_="BlockItem")
        for block in blocks:
            link = block.find('a')['href']
            self.movies.append(link)
        self.movies.reverse()

    def getSeasons(self, seasons):
        seasons_list = seasons.find_all('a')
        for season in seasons_list:
            self.seasons.append(season['href'])

        for season in self.seasons:
            self.getEpisodes(season)

    def getEpisodes(self, season):
        soup = self.makeRequest(season)
        episodes_list = soup.find_all('div', "BlockItem")
        videos = []
        for episode in episodes_list:
            videos.append(episode.a['href'])
        videos.reverse()
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
        link = url
        img_elem = soup.find('div', class_="Poster").img
        img_src = img_elem['data-src']
        title = soup.find('h2', class_="postTitle").text
        video = {'title': title, 'image': img_src,
                 'rating': "", 'notes': '-', 'link': link}
        return video

    def getWatchLinks(self, url):
        soup = self.makeRequest(url)

        watch_section = soup.find('div', class_="ServersEmbeds")
        watch_list = watch_section.find('ul')
        servers_name = watch_list.find_all('li')
        servers_link = watch_list.find_all('iframe')
        links = []
        for idx in range(len(servers_name)):
            name = servers_name[idx].text
            link = servers_link[idx]['data-srcout'].replace('\n', '')
            links.append({"name": name, 'link': link})
        return links

    def getDownloadLinks(self, url):
        soup = self.makeRequest(url)

        form = soup.find('form', id="formDown")
        download_btns = form.find_all('button')
        links = []
        for download in download_btns:
            link = download['value'].replace('\n', '')
            name = download.span.text
            links.append({'name': name, 'quality': "", 'link': link})
        return links

    def clearData(self):
        self.movies.clear()
        self.seasons.clear()
        self.episodes.clear()

    def __del__(self):
        self.session.close()


# moviz = MovizLand('movizland.date')
# url = "https://movizland.date/%d8%aa%d8%ad%d9%85%d9%8a%d9%84-%d9%81%d9%8a%d9%84%d9%85-plane-2023-%d9%85%d8%aa%d8%b1%d8%ac%d9%85-hdcam/"
# moviz.setUrl(url)
# moviz.startScraping()
