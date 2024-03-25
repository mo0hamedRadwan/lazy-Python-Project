import requests
from bs4 import BeautifulSoup
from urllib import parse
from websites.UserAgent import userAgent
#from UserAgent import userAgent
import random


class MyCima():
    def __init__(self, domainName= "mycima.la"):
        self.session = requests.Session()
        self.proxies = self.getProxies()
        self.domainName = domainName
        self.movies = []
        self.seasons = []
        self.episodes = []

    def setUrl(self, url):
        if(self.domainName in url):
            self.soup = self.makeRequest(url)
            error404 = self.soup.find('notfound-404')
            if(error404 != None or len(url) <= 23):
                print("setUrl: Page Not Found in myciiima")
                exit()
            self.url = url
        else:
            print("setUrl: Wrong Domain Name Or URL")
            exit()

    def searchBy(self, keywords):
        keywords = parse.quote_plus(keywords)
        urls = [f'https://{self.domainName}/search/{keywords}',
                f'https://{self.domainName}/search/{keywords}/list/series/']
        result = []
        for url in urls:
            soup = self.makeRequest(url)
            blocks = soup.find_all('div', class_="GridItem")
            for block in blocks:
                item = block.find('a')
                link = item['href']
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
        list_episodes = self.soup.find(
            'div', class_="Episodes--Seasons--Episodes")
        hasdivider = self.soup.find('singlerelated', class_="hasdivider")
        if(list_episodes != None):  # Series
            self.getSeasons()
        elif(hasdivider != None):
            link = hasdivider.find('a')['href']
            self.getMovies(link)
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

    def getMovies(self, url):
        soup = self.makeRequest(url)
        slider = soup.find('div', class_="Slider--Grid")
        movies_list = slider.find_all('div', class_="Thumb--GridItem")
        for movie in movies_list:
            link = movie.find('a')['href']
            print(link)
            self.movies.append(link)

    def getSeasons(self):
        list_seasons = self.soup.find('div', class_="List--Seasons--Episodes")
        if(list_seasons != None):
            seasons_links = list_seasons.find_all('a')
            for season in seasons_links:
                self.seasons.append(season['href'])
        else:
            season = self.soup.find('singlesection', class_="Series--Section")
            if(season == None):
                self.seasons.append(self.url)
            else:
                season_link = season.find('a')['href']
                self.seasons.append(season_link)
                
        for season in self.seasons:
            self.getEpisodes()

    def getEpisodes(self, season):
        soup = self.makeRequest(season)
        episodes_list = soup.find(
            'div', class_="Episodes--Seasons--Episodes")
        episodes_links = episodes_list.find_all('a')
        videos = []
        for episode in episodes_links:
            print(episode['href'])
            videos.append(episode['href'])
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
        title = soup.find('div', class_="Title--Content--Single-begin").text.strip()
        video = {'title': title, 'image': "",
                 'rating': "", 'notes': '-', 'link': link}
        return video

    def getWatchLinks(self):
        watch_servers = self.soup.find('ul', class_="WatchServersList")
        servers_list = watch_servers.find_all('li')
        links = []
        for server in servers_list:
            link = server.btn['data-url'].replace('\n', '')
            name = server.strong.text
            links.append({'name': name, 'link': link})
            #print(f'{name} : {link}')
        return links

    def getDownloadLinks(self, url):
        response = self.makeRequest(url)
        soup = BeautifulSoup(response, 'lxml')

        download_servers = soup.find(
            'ul', class_="List--Download--Mycima--Single")
        servers_list = download_servers.find_all('li')
        links = []
        print(len(servers_list))
        for server in servers_list:
            link = server.a['href']
            name = server.a.find('resolution').text
            links.append({'name': name, 'quality': "", 'link': link})
            print(f'Mycima ({name}) : {link}')
        return links

    def clearData(self):
        self.movies.clear()
        self.seasons.clear()
        self.episodes.clear()

    def __del__(self):
        self.session.close()


# mycima = MyCima('mycima.la')
# url = "https://www.mycima.la/watch/%d9%85%d8%b4%d8%a7%d9%87%d8%af%d8%a9-%d9%81%d9%8a%d9%84%d9%85-tick-tick-boom-2021-%d9%85%d8%aa%d8%b1%d8%ac%d9%85/"
# mycima.setUrl(url)
# mycima.startScraping()
