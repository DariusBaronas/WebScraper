from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import os

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

class WebScraper:

    def __init__(self):
        self.data = []



    def get_url(self, link_to_page, page_number):
        stored_urls = []
        for page in range(1, page_number):
            driver.get(link_to_page + str(page))
            response = driver.page_source
            soup = BeautifulSoup(response, 'html.parser')
            block = soup.find_all('tr', class_='list-row')
            for url in block:
                try:
                    stored_urls.append(url.a['href'])
                except:
                    pass
        return stored_urls

    def get_text(self, stored_urls):
        self.__get_price__get_address(stored_urls)

    def __get_dl(self, soup):
        d_list = {}
        for dl in soup.findAll("dl", {"class": "obj-details"}):
            for el in dl.find_all(["dt", "dd"]):
                if el.name == 'dt':
                    key = el.get_text(strip=True)
                elif key in ['Plotas:', 'Buto numeris:', 'Metai:', 'Namo numeris:', 'Kambarių sk.:', 'Aukštas:',
                             'Aukštų sk.:', 'Pastato tipas:', 'Šildymas:', 'Įrengimas:',
                             'Pastato energijos suvartojimo klasė:', 'Ypatybės:', 'Papildomos patalpos:',
                             'Papildoma įranga:', 'Apsauga:']:
                    d_list[key] = ' '.join(el.text.strip().replace("\n", ", ").split('NAUDINGA')[0].split('m²')[0].split())
        return d_list

    def __get_price__get_address(self, stored_urls):
        for address_text in stored_urls:
            driver.get(address_text)
            response = driver.page_source
            soup = BeautifulSoup(response, 'html.parser')
            price = soup.find('div', class_='price-left')
            address = soup.find('h1', 'obj-header-text')
            try:
                address1 = address.get_text(strip=True)
                address2 = re.findall(r'(.*),[^,]*$', address1)
                address = ''.join(address2)
                city, district, street = address.split(',')
            except:
                city, district, street = 'NaN'

            try:
                full_price = price.find('span', class_='price-eur').text.strip()
                full_price1 = full_price.replace('€', '').replace(' ', '').strip()
            except:
                full_price1 = 'NaN'

            try:
                price_sq_m = price.find('span', class_='price-per').text.strip()
                price_sq_m1 = price_sq_m.replace('€/m²)', '').replace('(domina keitimas)', '').replace('(', '').replace(' ', '').strip()
            except:
                price_sq_m1 = 'NaN'

            try:
                price_change = price.find('div', class_='price-change').text.strip()
                price_change1 = price_change.replace('%', '').strip()
            except:
                price_change1 = 'NaN'

            self.data.append({'City:': city, 'District:': district, 'Street:': street, 'Full_price, Eur:': full_price1, 'Price_m2, Eur:': price_sq_m1, 'Price_change, %:': price_change1, **self.__get_dl(soup)})


    def scrape_to_csv(self):
        os.makedirs('scraped_data', exist_ok=True)
        return pd.DataFrame(self.data).to_csv('scraped_data/output_vilnius.csv', index=False)







ws = WebScraper()
ws.get_text(ws.get_url('https://www.aruodas.lt/butai/vilniuje/puslapis/', 2))
ws.scrape_to_csv()
time.sleep(2)
driver.quit()
