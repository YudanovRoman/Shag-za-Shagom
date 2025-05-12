import sys
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import math
import sqlite3


weekday_dict = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


def check_datetime(dt, weekday, timed):
    date = False
    time = False
    if "ежедневно" in dt:
        date = True
        if "круглосуточно" in dt:
            time = True
        else:
            x = dt.split(", ")[1].split("–")
            x.append(timed)
    else:
        y = dt.split("; ")
        y = [i.split(" ") for i in y]
        for i in y:
            if weekday_dict.index(i[0][:2]) <= weekday <= weekday_dict.index(i[0][-2:]):
                date = True
                if "круглосуточно" in i[1]:
                    time = True
                else:
                    y = i[1].split("–")
                    y.append(timed)
                break
        if date and not time:
            for i in range(len(y)):
                y[i] = y[i][:2]
                if y[i][0] == "0":
                    y[i] = y[i][1]
                y[i] = int(y[i])
            num1, num2, num3 = y
            if num2 < num1:
                num2 += 24
            if num1 <= num3 <= num2 - 1:
                time = True
    if date and time:
        return True
    return False


def get_coords(name):
    geocoder_request = f'http://geocode-maps.yandex.ru/1.x/?apikey=8013b162-6b42-4997-9691-77b7074026e0&geocode={name}&format=json'
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coodrinates = toponym["Point"]["pos"]
        return ",".join(coodrinates.split(" "))


# Определяем функцию, считающую расстояние между двумя точками, заданными координатами
def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000 # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def get_organization_list(text, ll, num, weekday, time):
    search_params = {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": text,
        "lang": "ru_RU",
        "ll": ll,
        "type": "biz"
    }
    organizations = requests.get("https://search-maps.yandex.ru/v1/", params=search_params).json()["features"][:10]
    list_organizations = []
    for i in range(len(organizations)):
        organization = organizations[i]
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        org_address = organization["properties"]["CompanyMetaData"]["address"]
        point = organization["geometry"]["coordinates"]
        org_point = f"{point[0]},{point[1]}"
        if "Hours" in dict(organization["properties"]["CompanyMetaData"]).keys():
            if check_datetime(organization["properties"]["CompanyMetaData"]["Hours"]["text"], weekday, time):
                data = [org_name,
                        lonlat_distance([float(i) for i in ll.split(",")], [float(i) for i in org_point.split(",")]),
                        f"{org_point},pm2gnl{num}", org_point, organization]
                list_organizations.append(data)
    return list_organizations


class Route:
    def __init__(self, type, name, ll, weekday, time):
        self.type = type
        self.name = name
        self.names_org = []
        self.img = None
        self.address_ll = ll
        self.weekday = weekday
        self.time = time
        self.create_route()


    def create_route(self):
        points = self.address_ll
        for i in range(len(self.type)):
            org = get_organization_list(self.type[i], points, i + 1, self.weekday, self.time)
            self.names_org.append(min(org, key=lambda x: x[1]))
            points = self.names_org[-1][3]

    def create_img(self):
        apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
        map_params = {
            "apikey": apikey,
            "pt": f"{"~".join([i[2] for i in self.names_org])}",
            # "z": z
        }

        map_api_server = "https://static-maps.yandex.ru/v1"
        response = requests.get(map_api_server, params=map_params)
        self.img = BytesIO(response.content)
        opened_image = Image.open(self.img)
        return opened_image


# address_ll = get_coords(input("Страна, Город, Улица: "))
# address_ll = get_coords("Россия Липецк Свиридова 5")
# route = Route(["Парк Атракционов", "Кафе", "Парк"], "БАзовая прогулка", address_ll)
# route.create_img()


