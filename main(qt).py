from PyQt5 import QtWidgets, QtCore, QtGui
import webbrowser
import requests
import sys

# Website Modulues
from websites.Movizland import MovizLand
from websites.Shahid4u import Shahid4u
from websites.Cima4u import Cima4u
from websites.Mycima import MyCima

# Domains
MovizLand_domain = ""
Shahid4u_domain = ""
Cima4u_domain = ""
MyCima_domain = ""

# WebSite Objects
movizland = None
shahid4u = None
cima4u = None
mycima = None

def getDomains(fileName = "Domains.txt"):
    global MovizLand_domain, Shahid4u_domain, Cima4u_domain, MyCima_domain
    global movizland, shahid4u, cima4u, mycima

    with open(fileName, 'r') as file:
        domains = [domain for domain in file]

    for domain in domains:
        domain = domain.strip()
        if("movizland" in domain):
            MovizLand_domain = domain
        elif("shahed4u" in domain):
            Shahid4u_domain = domain
        elif("cima4u2" in domain):
            Cima4u_domain = domain
        elif("wecima2" in domain):
            MyCima_domain = domain
        else:
            pass

    # WebSite Objects
    movizland = MovizLand(MovizLand_domain)
    shahid4u = Shahid4u(Shahid4u_domain)
    cima4u = Cima4u(Cima4u_domain)
    mycima = MyCima(MyCima_domain)


class Window(QtWidgets.QWidget):
    def __init__(self, width, height, title="App"):
        super(Window, self).__init__()
        self.win = QtWidgets.QWidget()
        self.win.setFixedSize(width, height)
        self.win.setWindowTitle(title)
        self.tab = QtWidgets.QTabWidget(self.win)
        self.tab.setFixedSize(width, height)

    def getTab(self):
        return self.tab

    def show(self):
        self.win.show()


class Table(QtWidgets.QTableWidget):
    def __init__(self):
        super(Table, self).__init__()
        self.table = QtWidgets.QTableWidget()
        self.tableSetting1()
        self.data = []

    def tableSetting1(self):
        # Table Setting
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ['Image', 'Title', 'Rating', 'Notes', 'Link'])
        # Set Column Width
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 40)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 200)

    def tableSetting2(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Server', 'Quality', 'Link'])
        # Set Column Width
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 350)

    def getImgLabel(self, url: str):
        if(url == ""):
            url = "https://via.placeholder.com/100"
        imgLabel = QtWidgets.QLabel()
        imgLabel.setText("")
        imgLabel.setScaledContents(True)
        try:
            pixMap = QtGui.QPixmap()
            response = requests.get(url)
            pixMap.loadFromData(response.content, 'jpg')
            imgLabel.setPixmap(pixMap)
        except:
            pass
        return imgLabel

    def setItems1(self, items: list):
        self.data = items.copy()
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            # Set Row Height
            self.table.setRowHeight(row, 100)
            # self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item['image']))
            self.table.setCellWidget(row, 0, self.getImgLabel(item['image']))
            self.table.setItem(
                row, 1, QtWidgets.QTableWidgetItem(item['title']))
            self.table.setItem(
                row, 2, QtWidgets.QTableWidgetItem(item['rating']))
            self.table.setItem(
                row, 3, QtWidgets.QTableWidgetItem(item['notes']))
            self.table.setItem(
                row, 4, QtWidgets.QTableWidgetItem(item['link']))
        self.table.update()
        self.table.cellClicked.connect(self.itemClick)

    def setItems2(self, items: list):
        self.data = items.copy()
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            # Set Row Height
            self.table.setRowHeight(row, 20)
            self.table.setItem(
                row, 0, QtWidgets.QTableWidgetItem(item['name']))
            try:
                self.table.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(item['quality']))
            except:
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(""))
            self.table.setItem(
                row, 2, QtWidgets.QTableWidgetItem(item['link']))
        self.table.update()
        self.table.cellClicked.connect(self.itemClick2)

    def itemClick(self, row, col):
        self.movie_win = Window(600, 600, self.data[row]['title'])
        link = self.data[row]['link']

        self.download_t = Tab(self.movie_win.getTab(), "Download")
        self.download_t.tabLayout2()
        self.watch_t = Tab(self.movie_win.getTab(), "Watch")
        self.watch_t.tabLayout2()

        # Download and Watch Data
        self.download_list, self.watch_list = self.loadData(link)
        self.download_t.table.setItems2(self.download_list)
        self.watch_t.table.setItems2(self.watch_list)

        self.movie_win.show()

    def loadData(self, url):
        for website in (movizland, shahid4u, cima4u):
            if(website.domainName in url):
                d_links = website.getDownloadLinks(url)
                w_links = website.getWatchLinks(url)
                # print(w_links)
        return d_links, w_links

    def itemClick2(self, row, col):
        link = self.data[row]['link']
        webbrowser.open(link, new=2)


class Loading(QtWidgets.QWidget):
    def __init__(self):
        super(Loading, self).__init__()
        self.LoadingWindow = QtWidgets.QWidget()
        self.loadingLabel = QtWidgets.QLabel("XXX", self.LoadingWindow)
        # self.LoadingWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.LoadingSetting()

    def LoadingSetting(self):
        self.LoadingWindow.setFixedSize(100, 100)
        self.loadingLabel.resize(100, 100)

        self.movie = QtGui.QMovie("img/loading.gif")
        self.loadingLabel.setMovie(self.movie)

    def startAnimation(self):
        self.LoadingWindow.show()
        self.movie.start()

    def stopAnimation(self):
        self.movie.stop()
        self.LoadingWindow.close()


class Tab(QtWidgets.QWidget):
    def __init__(self, par: QtWidgets.QTabWidget, name: str):
        super(Tab, self).__init__()
        self.name = name
        self.par = par
        self.tab = QtWidgets.QWidget(par)
        par.addTab(self.tab, name)
        # self.tabLayout1()

    def tabLayout1(self, placeholder: str = ""):
        vLayout = QtWidgets.QVBoxLayout(self.tab)
        hLayout = QtWidgets.QHBoxLayout()
        self.table = Table()
        self.table.tableSetting1()

        self.lineEdit = QtWidgets.QLineEdit()
        self.pushBtn = QtWidgets.QPushButton(self.name)

        self.placeholder = placeholder
        self.lineEdit.setPlaceholderText(self.placeholder)

        hLayout.addWidget(self.lineEdit)
        hLayout.addWidget(self.pushBtn)
        vLayout.addLayout(hLayout)
        vLayout.addWidget(self.table.table)

        self.pushBtn.setShortcut(QtCore.Qt.Key_Return)
        self.pushBtn.clicked.connect(self.btnClick)

    def tabLayout2(self):
        vLayout = QtWidgets.QVBoxLayout(self.tab)
        self.table = Table()
        vLayout.addWidget(self.table.table)
        self.table.tableSetting2()

    def btnClick(self):
        if(self.name == 'Download'):
            self.btnDownloadClick(self.lineEdit.text())
        else:
            self.btnSearchClick(self.lineEdit.text())

    def scrapingUrl(self, url):
        self.output = []
        for website in (movizland, shahid4u, cima4u):
            if(website.domainName in url):
                # print(website.domainName)
                website.setUrl(url)
                #{'title', 'image', 'rating', 'notes', 'link'}
                self.output = website.startScraping()
                # print(output)
                website.clearData()

    def btnDownloadClick(self, text):
        print("Download")
        msg = QtWidgets.QMessageBox()
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        if('http' in text):
            self.scrapingUrl(text)

            if(not self.output):
                # Stop Loading

                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle("Access Website")
                msg.setText(
                    "Sorry, Program Can't Access this type of URL\nContact Developer to Update or solve this problem")

                msg.exec_()
                print("Don't Accessed this type of URL")
            else:
                self.table.setItems1(self.output)
                self.output.clear()
                # Stop Loading

        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Invalid URL")
            msg.setText("Invalid URL")
            msg.exec_()
            print("Invalid URL")
        print("Finish")

    def btnSearchClick(self, text):
        print("Search")
        if(text):
            # Start Loading

            self.output = []
            for website in (cima4u, mycima):
                self.output.extend(website.searchBy(text))
                # print(output)
            self.table.setItems1(self.output)
            self.output.clear()
            # End Loading

        else:
            msg = QtWidgets.QMessageBox()
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Empty Text")
            msg.setText("Please Insert Some Words To Search.")
            msg.exec_()
        print("finish")
    

if __name__ == "__main__":
    getDomains()
    app = QtWidgets.QApplication([])
    win = Window(800, 600, "LazySkipper")
    d_tab = Tab(win.getTab(), name="Download")
    d_tab.tabLayout1(
        placeholder="Enter Url like : https://movizland.xyz/blablabla")
    s_tab = Tab(win.getTab(), name="Search")
    s_tab.tabLayout1(placeholder="Enter Movie or Series Name like : Avengers")

    win.show()
    sys.exit(app.exec_())
