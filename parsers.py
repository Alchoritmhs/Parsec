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
import re
from json import loads

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
    urllib3.util.ssl_.DEFAULT_CIPHERS = my_ciphers
except:
    raise exit(0)


def make_request(url):
    with requests.session() as session:
        session.mount('https://', MyAdapter())
        session.headers = headers_avito
        session.verify = False
        return session.get(url)


def make_request_yandex(url, params, headers):
    with requests.session() as session:
        session.mount('https://', MyAdapter())
        session.headers = headers
        session.verify = False
        return session.get(url, params=params)


api_key = 'cb408d30-83d7-41b8-85c9-d6a544d1c64d'
api_key_org = 'ece3dc91-6a21-4460-875c-430ae25ea3f3'

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

headers_ozon = CaseInsensitiveDict()
headers_ozon["authority"] = "www.ozon.ru"
headers_ozon["accept"] = "application/json"
headers_ozon["x-o3-app-name"] = "dweb_client"
headers_ozon["$x-o3-app-version"] = "hotfix_20-10'-'2020_3bb97afd"
headers_ozon[
    "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
headers_ozon["sec-fetch-site"] = "same-origin"
headers_ozon["sec-fetch-mode"] = "cors"
headers_ozon["sec-fetch-dest"] = "empty"
headers_ozon["referer"] = "https://www.ozon.ru/"
headers_ozon["accept-language"] = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6"


def get_coordinates(city):
    url = 'https://geocode-maps.yandex.ru/1.x/'
    params = (
        ('apikey', api_key),
        ('geocode', city),
        # ('format', 'json')
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
    url = f"https://api.youla.io/api/v1/mapsme/suggest?app_id=web%2F2&uid=5fc1711b18b04&timestamp=1606512959490&q={city_encoded}&format=json&rank=4&limit=10"

    request = requests.get(url, headers=headers_youla)
    json = request.json()
    city_id = None
    for i in json['results']:
        if city in i['name']:
            city_id = i['id']
            break

    return city_id


def get_location_id(city):
    city_encoded = quote(city)
    url = f"https://www.ozon.ru/api/location/v2/search?query={city_encoded}"

    request = requests.get(url, headers=headers_ozon)
    json = request.json()
    city_id = None
    for i in json:
        if city in i['name']:
            city_id = i['areaId']
            break

    return city_id


def get_pickups_ozon(city):
    city_id = get_location_id(city)
    url = f'https://www.ozon.ru/api/composer-api.bx/_action/cmsGetPvzV2?areaID={city_id}'

    request = requests.get(url, headers=headers_ozon)
    json = request.json()
    return len(json['pvzs'])


def get_it_comp_by_city(city):
    url = 'https://search-maps.yandex.ru/v1/'
    params = (
        ('apikey', api_key_org),
        ('text', f'IT-компания, {city}'),
        ('lang', 'ru_RU'),
        ('format', 'json'),
        ('results', 500)
    )
    count = 0
    skip = 0
    request = requests.get(url, params=params)
    json = request.json()
    while len(json['features']) != 0:
        skip += 500
        count += len(json['features'])
        request = requests.get(url + f'?skip={skip}', params=params)
        if request.status_code == 200:
            json = request.json()
        else:
            break

    return count


def get_city_info(city):
    url = f'https://ru.wikipedia.org/wiki/{quote(city)}'
    request = requests.get(url)
    soup = bs4.BeautifulSoup(request.text, 'lxml')
    population = soup.find('span', {'data-wikidata-property-id': 'P1082'}).text.strip().split('[')[0]
    population = ''.join(re.findall('\d+', population))
    square = soup.find('span', {'data-wikidata-property-id': 'P2046'}).text.strip().split('[')[0]
    square = ''.join(re.findall('\d+', square))
    return [population, square]


def get_sber_market_retailers(city):
    request = requests.get('https://sbermarket.ru/')
    soup = bs4.BeautifulSoup(request.text, 'lxml')
    slug = None
    json = loads(soup.find('div', {'data-react-class': "HomeLanding"}).get('data-react-props'))
    for i in json.get('pageProps').get('cities'):
        if i.get('name') == city:
            slug = i.get('slug')

    url = f"https://sbermarket.ru/cities/{slug}"
    headers = CaseInsensitiveDict()
    headers["authority"] = "sbermarket.ru"
    headers["cache-control"] = "max-age=0"
    headers["upgrade-insecure-requests"] = "1"
    headers[
        "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    headers[
        "accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["sec-fetch-site"] = "same-origin"
    headers["sec-fetch-mode"] = "navigate"
    headers["sec-fetch-user"] = "?1"
    headers["sec-fetch-dest"] = "document"
    headers["referer"] = "https://sbermarket.ru/cities/arhangelsk"
    headers["accept-language"] = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6"
    request = requests.get(url, headers=headers)

    count = 0
    if request.status_code == 200:
        soup = bs4.BeautifulSoup(request.text, 'lxml')
        count = len(soup.find_all('div', {'class': 'description_37VdV'}))
    else:
        pass

    return count


cats = ['Город', 'Личные вещи', 'Транспорт', 'Для дома и дачи', 'Хобби и отдых', 'Бытовая электроника',
        'Работа', 'Услуги', 'Готовый бизнес и оборудование', 'Всего объявлений по выбранным категориям',
        'Всего объявлений']
line = ['Город', 'Количество пунктов выдачи']
line_it = ['Город', 'Количество ИТ-компаний']
line_info = ['Город', 'Население', 'Площадь']
line_sber = ['Город', 'Количество компаний, сотрудничающи со Сбер-Маркет']
cities = ['Магадан', 'Екатеринбург', 'Волгоград', 'Сочи', 'Сургут', 'Краснодар']

csv_writer('sber_reatilers', [line_sber])

for i in cities:
    data = get_sber_market_retailers(i)
    csv_writer('sber_reatilers', [[i, data]])

# csv_writer('cities_info', [line_info])
#
# for i in cities:
#     data = get_city_info(i)
#     csv_writer('cities_info', [[i] + data])

# csv_writer('ozon_pickups', [line])
#
# for i in cities:
#     data = get_pickups_ozon(i)
#     csv_writer('ozon_pickups', [[i, data]])

# csv_writer('it_companies', [line])
#
# for i in cities:
#     data = get_it_comp_by_city(i)
#     csv_writer('it_companies', [[i, data]])


# csv_writer('avito', [cats])
# for i in cities:
#     data = get_total_by_cats_avito(i)
#     csv_writer('avito', [data])
