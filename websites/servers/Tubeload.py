from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


class Tureload():
    def __init__(self):
        PATH = "../../webdriver/chromedriver.exe"
        self.driver = webdriver.Chrome(service=Service(
            PATH), options=self.getDriverOptions())

    def getDownlaodLink(self, url):
        self.driver.get(url)
        time.sleep(5)
        section = self.driver.find_element(By.CLASS_NAME, "col-md-4")
        btn = section.find_element(By.CSS_SELECTOR, "a")
        self.driver.execute_script("""
            btn = document.querySelector(".col-md-4 a")
            btn.click()
        """)
        time.sleep(7)
        link = btn.get_attribute("href")
        print(link)
        return link

    def getDriverOptions(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        options.add_argument('--start-maximized')
        options.add_argument('--incognito')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument("--mute-audio")

        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-gpu")

        # options.add_argument('user-agent={userAgent}')
        # options.add_argument('proxy-server={}'.format(self.proxy_server))
        return options

    def __del__(self):
        # self.driver.close()
        pass


tureload = Tureload()
tureload.getDownlaodLink('https://tubeload.co/f/zypunl8czisq/m3gan.2022.mp4')
