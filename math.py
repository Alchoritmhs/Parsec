import csv


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


def csv_reader(platform, data):
    """
    Функция для чтения записей из CSV
    """
    with open(f'{platform[0]}.csv', "r", newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        i = 0
        for elem in reader:
            if i != 0:
                data.get(elem[0]).append(elem[1])
                data.get(elem[0]).append(elem[2])
            i += 1
    with open(f'{platform[1]}.csv', "r", newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        i = 0
        for elem in reader:
            if i != 0:
                data.get(elem[0]).append(elem[10])
            i += 1
    with open(f'{platform[2]}.csv', "r", newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        i = 0
        for elem in reader:
            if i != 0:
                data.get(elem[0]).append(elem[1])
            i += 1
    return data


cats = ['Город', 'Население', 'Площадь', 'Всего объявлений', 'Количество пунктов выдачи', 'Субиндекс']
cities = ['Магадан', 'Екатеринбург', 'Волгоград', 'Сочи', 'Сургут', 'Краснодар']
data = {
    'Магадан': [],
    'Екатеринбург': [],
    'Волгоград': [],
    'Сочи': [],
    'Сургут': [],
    'Краснодар': []
}
platforms = ['data/cities_info', 'data/avito', 'data/ozon_pickups']
csv_writer('data/math', [cats])
data = csv_reader(platforms, data)
for city in cities:
    line = data.get(city)
    data.get(city).append(round((((4*int(line[2]))/int(line[0]))+((2*int(line[3]))/int(line[1])))/2, 2))
    csv_writer('data/math', [data.get(city)])
