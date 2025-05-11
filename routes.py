import sys
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import math
import sqlite3


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


def get_organization_list(text, ll, num):
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
        data = []
        organization = organizations[i]
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        data.append(org_name)
        org_address = organization["properties"]["CompanyMetaData"]["address"]
        point = organization["geometry"]["coordinates"]
        org_point = f"{point[0]},{point[1]}"
        data.append(
            lonlat_distance([float(i) for i in ll.split(",")], [float(i) for i in org_point.split(",")]))
        if "Hours" not in dict(organization["properties"]["CompanyMetaData"]).keys():
            data.append(f"{org_point},pm2grl{num}")
        elif "круглосуточно" in organization["properties"]["CompanyMetaData"]["Hours"]["text"].lower():
            data.append(f"{org_point},pm2gnl{num}")
        else:
            data.append(f"{org_point},pm2lbl{num}")
        data.append(org_point)
        list_organizations.append(data)
    return list_organizations


class Route:
    def __init__(self, route_type=False, name=False, description=False, ll=False, creator_id=False, route_id=-1):
        if route_type >= 0:
            self.route_id = route_id
            self.get_by_id()
            self.type = []
        else:
            self.type = route_type
            self.table_name = 'data.db'
            self.creator_id = creator_id
            self.name = name
            self.description = description
            self.names_org = []
            self.img = None
            self.address_ll = ll
            self.route_id = self.create_route()
            self.create_img()
            self.commit()

    def create_route(self):
        points = self.address_ll
        for i in range(len(self.type)):
            org = get_organization_list(self.type[i], points, i + 1)
            self.names_org.append(min(org, key=lambda x: x[1]))
            points = self.names_org[-1][3]
        con = sqlite3.connect(f'static/sqLite3/{self.table_name}.db')
        cur = con.cursor()
        max_id = cur.execute("""SELECT MAX(id) FROM routes""").fetchone()
        con.close()
        return max_id + 1

    def create_img(self):
        apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
        map_params = {
            "apikey": apikey,
            "pt": f"{'~'.join([i[2] for i in self.names_org])}~{self.address_ll},round",
            #    "z": z
        }

        map_api_server = "https://static-maps.yandex.ru/v1"
        response = requests.get(map_api_server, params=map_params)
        self.img = BytesIO(response.content)
        opened_image = Image.open(self.img)
        opened_image.save(f"static/img/route_{self.route_id}.png")
        # opened_image.save("example.png")

    def commit(self):
        con = sqlite3.connect(f'static/sqLite3/{self.table_name}.db')
        cur = con.cursor()

        cur.execute('''INSERT INTO routes(id, creator_id, places_list, name, description) VALUES (?,?,?,?,?)''',
                    (self.route_id, self.creator_id, ';'.join(self.names_org), self.name, self.description))
        con.commit()
        con.close()

    def get_by_id(self):
        con = sqlite3.connect(f'static/sqLite3/{self.table_name}.db')
        cur = con.cursor()



        self.names_org, self.creator_id, self.name, self.description = cur.execute(
            '''SELECT places_list, creator_id, name, description FROM routes WHERE id=?''', (self.route_id,)
        )

        con.close()


# address_ll = get_coords(input("Страна, Город, Улица: "))
address_ll = get_coords("Россия Липецк Свиридова 5")
route = Route(["Парк Атракционов", "Кафе", "Парк"], "Базовая прогулка",
              'Лучший вариант, что-бы развеятся после школы', address_ll)
route.create_img()


# con = sqlite3.connect("static/sqLite3/Thumbs.db")
# cur = con.cursor()
# id = cur.execute("""SELECT MAX(id) FROM routes""").fetchone()
# print(id[0])
# cur.execute(f"""INSERT INTO routes(id, creator_id)""").fetchall()
# con.commit()
# con.close()
# #opened_image.show()