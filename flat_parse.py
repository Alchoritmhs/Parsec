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
    number = all_number = soup.find('span', {'class': 'Button__text'}).text[9:]
    number = str[:str.find('о')-1]
    print(number)
    return number


def take_online_info(url):
    """
        Функция для находения онлайн объявлений
    """
    browser.get(url)
    time.sleep(1)
    requiredhtml = browser.page_source
    soup = BeautifulSoup(requiredhtml, 'html5lib')
    elems = soup.find_all('div', {'class': 'TagHighlight__container--3IISv TagHighlight__green--6Fono pEqrL38BluF4aqgItem__itemTag'})
    number = 0
    for elem in elems:
        if elem.text == 'Готовы показать онлайн':
            number += 1
    return number


cats = ['City', 'Number of offers', 'Online offers']
cities = ['Магадан', 'Екатеринбург', 'Волгоград', 'Сочи', 'Сургут', 'Краснодар']
urls_for_search = {'Магадан': 'https://realty.yandex.ru/magadan/kupit/kvartira/',
                   'Екатеринбург': 'https://realty.yandex.ru/ekaterinburg/kupit/kvartira/',
                   'Волгоград': 'https://realty.yandex.ru/volgograd/kupit/kvartira/',
                   'Сочи': 'https://realty.yandex.ru/sochi/kupit/kvartira/',
                   'Сургут': 'https://realty.yandex.ru/surgut/kupit/kvartira/ ',
                   'Краснодар': 'https://realty.yandex.ru/krasnodar/kupit/kvartira/'}
csv_writer('flats', [cats])
csv_writer('flats', [['test', '123', '23']])
for city in cities:
    number_of_offers = take_offers_info(urls_for_search.get(city))
    online_offers = take_online_info(urls_for_search.get(city))
    data = [city, number_of_offers, online_offers]
    csv_writer('flats', [data])
browser.close()

