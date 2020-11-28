import requests
from requests.structures import CaseInsensitiveDict
import xmltodict
from urllib.parse import quote
import bs4
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2)


try:
    urllib3.util.ssl_.DEFAULT_CIPHERS = 'Ciphers)'
except:
    raise exit(0)


def make_request(url):
    with requests.session() as session:
        session.mount('https://', MyAdapter())
        session.headers = headers_avito
        session.verify = False
        return session.get(url)


api_key = 'cb408d30-83d7-41b8-85c9-d6a544d1c64d'

headers_avito = CaseInsensitiveDict()
headers_avito["authority"] = "www.avito.ru"
headers_avito["accept"] = "application/json"
headers_avito["x-source"] = "client-browser"
headers_avito[
    "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
headers_avito["content-type"] = "application/json"
headers_avito["sec-fetch-site"] = "same-origin"
headers_avito["referer"] = "https://www.avito.ru/moskva"
headers_avito["accept-language"] = "ru-RU,ru;q=0.9"


headers_youla = CaseInsensitiveDict()
headers_youla["Connection"] = "keep-alive"
headers_youla["X-Youla-Splits"] = "8a=5|8b=3|8c=0|8m=0|16a=0|16b=0|64a=3|64b=0|100a=82|100b=63|100c=0|100d=0|100m=0"
headers_youla["Accept"] = "application/json, text/plain, */*"
headers_youla[
    "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
headers_youla["Origin"] = "https://youla.ru"
headers_youla["Sec-Fetch-Site"] = "cross-site"
headers_youla["Sec-Fetch-Mode"] = "cors"
headers_youla["Sec-Fetch-Dest"] = "empty"
headers_youla["Referer"] = "https://youla.ru/"
headers_youla["Accept-Language"] = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6"


def get_coordinates(city):
    url = 'https://geocode-maps.yandex.ru/1.x/'
    params = (
        ('apikey', api_key),
        ('geocode', city),
    )
    request = requests.get(url, params=params)
    json = xmltodict.parse(request.text, process_namespaces=True)
    try:
        coordinates = json['http://maps.yandex.ru/ymaps/1.x:ymaps'] \
            ['http://maps.yandex.ru/ymaps/1.x:GeoObjectCollection'] \
            ['http://www.opengis.net/gml:featureMember'] \
            ['http://maps.yandex.ru/ymaps/1.x:GeoObject'] \
            ['http://www.opengis.net/gml:Point'] \
            ['http://www.opengis.net/gml:pos']
    except:
        coordinates = json['http://maps.yandex.ru/ymaps/1.x:ymaps'] \
            ['http://maps.yandex.ru/ymaps/1.x:GeoObjectCollection'] \
            ['http://www.opengis.net/gml:featureMember'][0] \
            ['http://maps.yandex.ru/ymaps/1.x:GeoObject'] \
            ['http://www.opengis.net/gml:Point'] \
            ['http://www.opengis.net/gml:pos']
    return coordinates.split(' ')


def get_location_id_avito(city):
    city_encoded = quote(city)
    request = make_request(f"https://www.avito.ru/web/1/slocations?q={city_encoded}")
    json = request.json()['result']['locations']

    city_id = None
    for i in json:
        if city in i['names']['1']:
            city_id = i['id']
            break

    return city_id


def get_total_avito(city):
    # coordinates = get_coordinates(city)
    city_id = get_location_id_avito(city)
    params = (
        ('cd', 0),
        ('s', 101),
        ('countOnly', 1),
        # ('cataloggeoCoords', '%2C'.join(reversed(coordinates))),
        ('locationId', city_id),
    )
    url = "https://www.avito.ru/js/catalog"

    request = requests.get(url, headers=headers_avito, params=params)
    json = request.json()
    return json['totalCount'], json['url']


def get_total_by_cats_avito(city):
    total_count, slug = get_total_avito(city)
    request = make_request('https://www.avito.ru' + slug)

    soup = bs4.BeautifulSoup(request.text, 'lxml')
    data = soup.find_all('div', {'class': 'category-with-counters-item-1D4Vp'})

    data_file = []
    data_file.append(city)
    for cat in cats:
        for i in data:
            if i.find('a').text.strip() == cat:
                data_file.append(int(i.find('span').text.strip().replace(',', '')))
    data_file.append(sum(data_file[1:]))
    data_file.append(total_count)
    return data_file


def get_location_id_youla(city):
    city_encoded = quote(city)
    url = "https://api.youla.io/api/v1/mapsme/suggest?app_id=web%2F2&uid=5fc1711b18b04&timestamp=1606512959490&q=%D0%BF%D1%81%D0%BA%D0%BE%D0%B2&format=json&rank=4&limit=10"

    request = requests.get(url, headers=headers_youla)
    json = request.json()
    city_id = None
    for i in json['results']:
        if city in i['name']:
            city_id = i['id']
            break

    return city_id

get_location_id_youla('Псков')

# cats = ['Город', 'Личные вещи', 'Транспорт', 'Для дома и дачи', 'Хобби и отдых', 'Бытовая электроника',
#         'Работа', 'Услуги', 'Готовый бизнес и оборудование', 'Всего объявлений по выбранным категориям',
#         'Всего объявлений']
# cities = ['Магадан', 'Екатеринбург', 'Волгоград', 'Сочи', 'Сургут', 'Краснодар']
# csv_writer('avito', [cats])
# for i in cities:
#     data = get_total_by_cats_avito(i)
#     csv_writer('avito', [data])
