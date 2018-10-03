from bs4 import BeautifulSoup
from requests import get
from base64 import decodebytes
from copy import copy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui
from json import loads


class Command:

    description = None
    title = None
    prefix = None
    optional = False
    driver = False

    def get_title(self):
        return self.title

    def get_prefix(self):
        return self.prefix

    def get_description(self):
        return self.description


class Thuisbezorgd(Command):

    optional = True
    prefix = "!eten"
    title = "Thuisbezorgd Restaurants [!eten postcode]"
    description = "Zoekt de actuele restaurants op in een postcode."

    def run(self, zipcode):
        info = ""
        req = get('https://www.thuisbezorgd.nl/{}'.format(zipcode))
        source = req.content
        soup = BeautifulSoup(source, 'html.parser')
        elements = soup.find_all('div', class_='restaurant grid')
        for e in elements:
            try:
                soup = BeautifulSoup(str(e), 'html.parser')
                restaurant = soup.find('a', class_='restaurantname').text.strip()
                open = soup.find('div', class_='open').text
                open = open if len(open) > 0 else "open"
                avg = soup.find('div', class_='avgdeliverytime').text
                min = soup.find('div', class_='min-order').text
                info += "*{}*\nGemiddelde bezorgtijd: {}\nMinimale bestelbedrag: {}\n{}\n\n"\
                    .format(restaurant, avg, min, open)

            except AttributeError:
                pass
        if info is not None:
            return info


class LaatsteNieuws(Command):

    prefix = "!laatstenieuws"
    title = "De Laatste Headlines [!laatstenieuws]"
    description = "Haalt het meest recente nieuws op van nu.nl."

    def run(self):
        info = ""
        req = get('https://www.nu.nl/net-binnen')
        source = req.content
        soup = BeautifulSoup(source, 'html.parser')
        elements = soup.find_all('span', class_='info')
        for e in elements[:3]:
            try:
                soup = BeautifulSoup(str(e), 'html.parser')
                timestamp = soup.find('span', class_='timestamp').text.strip()
                titel = soup.find('span', class_='title-wrapper').text.strip()
                description = soup.find('span', class_='excerpt').text.strip()
                info += "*{}*\n{}\n\n{}\n\n"\
                    .format(titel, timestamp, description)
            except AttributeError:
                pass

        return info


class Screenshot(Command):

    optional = True
    driver = True
    prefix = "!screenshot"
    title = "Google Screenshotter [!screenshot omschrijving]"
    description = "Zoekt in Google op de omschrijving en maakt een screenshot."

    def run(self, driver, params):
        driver.execute_script("window.open('','_blank');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get('https://www.google.nl/search?q={}&num=100&source=lnms&tbm=isch&sa=X'.format(params))
        while driver.execute_script("return document.readyState;") != "complete":
            pass
        pyautogui.hotkey('printscreen')
        driver.close()  # close window
        driver.switch_to.window(driver.window_handles[0])
        ActionChains(driver)\
            .key_down(Keys.CONTROL)\
            .send_keys('v')\
            .key_up(Keys.CONTROL)\
            .pause(2)\
            .send_keys(Keys.RETURN)\
            .perform()


class Weersverwachting(Command):

    optional = True
    prefix = "!weer"
    title = "Weersverwachting Inzien [!weer plaats]"
    description = "Zoekt de weersverwachting van vandaag op."

    def run(self, params):
        req = get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'
                  .format(params, 'f6eeb6755658827d6cb52468a02a7672'))
        source = req.content
        json = loads(source)
        try:
            return "Het is nu *{}* graden in *{}*.".format(json['main']['temp'], params)
        except KeyError:
            return "Helaas, ik heb de weersverwachting niet kunnen ophalen."


class Bieraanbieding(Command):

    optional = True
    prefix = "!bier"
    title = "Bier in de aanbieding [!bier aantal]"
    description = "Haalt alle bier aanbiedingen op van Biernet. Maximaal 100 aanbiedingen."

    def run(self, params):
        params = int(params)
        if params > 100:
            params = 100
        req = get('https://www.biernet.nl/bier/aanbiedingen?s=kortingspercentage')
        source = req.content
        soup = BeautifulSoup(source, 'html.parser')
        elements = soup.find_all('div', class_='textaanbieding')
        msg = ""
        for element in elements[:params]:
            soup = BeautifulSoup(str(element), 'html.parser')
            merk = soup.find('span', class_='merk').text
            hoeveelheid = soup.find('p').text
            oudeprijs = soup.find('del').text
            prijs = soup.find('span', class_='prijs').text
            winkel = soup.find('img')['alt']
            msg += '*{} {}*\nWinkel: {}\nVan {} voor {}\n\n'.format(merk, hoeveelheid, winkel, oudeprijs, prijs)
        return msg


class Fap(Command):

    prefix = "!fap"
    title = "Fap Randomizer [!fap]"
    description = "Voor de verveelde mastrubeerder."

    def run(self):
        req = get('https://www.pornhub.com/random')
        return "{}".format(req.url)
