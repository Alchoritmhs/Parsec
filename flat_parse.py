import time
from bs4 import BeautifulSoup
from selenium import webdriver
import csv
chromedriver = 'chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)


def csv_writer(platform, data):
    """
    Функция для записи данных в CSV
    """
    with open(f'{platform}.csv', "a", newline='', encoding='utf-8') as csv_file:
        '''
        csv_file - объект с данными
        delimiter - разделитель
        '''
        writer = csv.writer(csv_file, delimiter=';')
        for line in data:
            writer.writerow(line)


def take_offers_info(url):
    """
        Функция для нахождения числа всех объявлений
    """
    browser.get(url)
    time.sleep(1)
    requiredhtml = browser.page_source
    soup = BeautifulSoup(requiredhtml, 'html5lib')
    number = soup.find('span', {'class': 'Button__text'}).text[9:]
    number = number[:number.find('о')-1]
    return number


def take_online_info(url):
    """
        Функция для находения онлайн объявлений
    """
    number = 0
    for i in range(26):
        browser.get(url)
        time.sleep(1)
        requiredhtml = browser.page_source
        soup = BeautifulSoup(requiredhtml, 'html5lib')
        elems = soup.find_all('div', {'class': 'TagHighlight__container--3IISv TagHighlight__green--6Fono pEqrL38BluF4aqgItem__itemTag'})
        for elem in elems:
            if elem.text == 'Готовы показать онлайн':
                number += 1
        url = url + '?page=' + i
    return number


cats = ['Город', 'Количество предложений', 'Количество онлайн предложений']
cities = ['Магадан', 'Екатеринбург', 'Волгоград', 'Сочи', 'Сургут', 'Краснодар']
urls_for_search = {'Магадан': 'https://realty.yandex.ru/magadan/kupit/kvartira/',
                   'Екатеринбург': 'https://realty.yandex.ru/ekaterinburg/kupit/kvartira/',
                   'Волгоград': 'https://realty.yandex.ru/volgograd/kupit/kvartira/',
                   'Сочи': 'https://realty.yandex.ru/sochi/kupit/kvartira/',
                   'Сургут': 'https://realty.yandex.ru/surgut/kupit/kvartira/ ',
                   'Краснодар': 'https://realty.yandex.ru/krasnodar/kupit/kvartira/'}
csv_writer('data/flats', [cats])
for city in cities:
    number_of_offers = take_offers_info(urls_for_search.get(city))
    online_offers = take_online_info(urls_for_search.get(city))
    data = [city, number_of_offers, online_offers]
    csv_writer('data/flats', [data])
browser.close()
