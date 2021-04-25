import os
import sys
import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from datetime import datetime
from translate import Translator
import threading


def good_morning(id):
    vk_session = vk_api.VkApi(
        token=TOKEN)
    vk = vk_session.get_api()
    vk.messages.send(user_id=id,
                     message='Доброе утро!',
                     random_id=random.randint(0, 2 ** 64))


def get_city_id(s_city_name):
    res = requests.get("http://api.openweathermap.org/data/2.5/find",
                       params={'q': s_city_name, 'type': 'like', 'units': 'metric', 'lang': 'ru', 'APPID': appid})
    data = res.json()
    city_id = data['list'][0]['id']
    return city_id


# Запрос текущей погоды
def request_current_weather(city_id):
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
    data = res.json()
    return [data['weather'][0]['description'], data['main']['temp']]


def get_time():
    time = datetime.now()
    ms = str(time.microsecond)
    time = time.strftime("%H:%M:%S")
    return "Точное время сейчас: " + time + '.' + ms[:3]


def get_date():
    time = datetime.now()
    time = time.strftime("%d-%m-%Y")
    return "Сегодняшняя дата: " + time


def translate(text, fr_l, to_l):
    translator = Translator(from_lang=fr_l, to_lang=to_l)
    result = translator.translate(text)
    return result


def photo_add(adress):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + adress + "&format=json"

    response = requests.get(geocoder_request)
    json_response = response.json()

    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]

    coords = toponym_coodrinates.replace(' ', ',')
    map_request = 'http://static-maps.yandex.ru/1.x/?ll=' + coords + '&spn=0.002,0.002&l=map'
    response = requests.get(map_request)

    if not response:
        return False
    return response.content


TOKEN = "506cec8c61fb8a22600b3e518b2a6d7951f51149cfc46ed9fa694a1b07f84ed445d0b382585766688dd1b"
appid = "c59e9b6d9a6a40fb0bd45b848404bf8a"
fr_l = 'Russian'
to_l = 'English'


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, 203721232)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            text = event.obj.message['text']
            vk = vk_session.get_api()
            if text[0] == '!':
                try:
                    text = text[1:]
                    if text[:4] == 'дата':
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=get_date(),
                                         random_id=random.randint(0, 2 ** 64))
                    elif text[:4] == 'типы':
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message='\n'.join(["1: линейное уравнение ax + b = 0",
                                                            "2: Квадратное уравнение ax² + bx + c == 0",
                                                            "3: решение системы ax + by + c = 0, dx + ey + f = 0"])
                                         ,
                                         random_id=random.randint(0, 2 ** 64))
                    elif text[:4] == 'язык':
                        lan1, lan2 = text.split()[1:]
                        fr_l = translate(lan1.capitalize(), 'Russian', 'English')
                        to_l = translate(lan2.capitalize(), 'Russian', 'English')
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message="Языки сохранены",
                                         random_id=random.randint(0, 2 ** 64))
                    elif text[:5] == 'время':
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=get_time(),
                                         random_id=random.randint(0, 2 ** 64))
                    elif text[:6] == 'погода':
                        try:
                            cityid = get_city_id(text[7:])
                            res = request_current_weather(cityid)
                            pogoda = res[0]
                            gradysi = res[1]
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message='Погода: ' + str(pogoda) + ', ' + str(gradysi) + '°C',
                                             random_id=random.randint(0, 2 ** 64))
                        except:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message='Неверное название города',
                                             random_id=random.randint(0, 2 ** 64))
                    elif text[:7] == 'слчисло':
                        text = text.split()[1:]
                        n = random.choice(list(range(int(text[0]), int(text[1]) + 1)))
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=n,
                                         random_id=random.randint(0, 2 ** 64))

                    elif text[:7] == 'команды':
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message='\n'.join(["Все команды бота:",
                                                            "!команды - получить список команд",
                                                            "!время - получить точное время в Екатеринбурге",
                                                            "!дата - получить точную дату",
                                                            "!погода <город> - получить погоду в городе",
                                                            "!перевод <фраза> - перевод заданной фразы на заданный язык",
                                                            "!язык <Исходный> <Результат> - задать языки для переводчика",
                                                            "!калькулятор <выражение> - вычисление простейших действий",
                                                            "!уравнение <тип> <арг1> <арг2> .. - решение уравнения, типы и агрументы можно получить с помощью !типы",
                                                            "!типы - получить информацию о вводе данных для уравнений",
                                                            "!слчисло <начало> <конец> - случайное целое число от начального числа до конечного",
                                                            "!будильник <число(необяз)> <час> <минута> - поставить таймер на заданное время"])
                                         ,
                                         random_id=random.randint(0, 2 ** 64))
                    elif text[:7] == 'перевод':
                        try:
                            mess = translate(text[8:], fr_l, to_l)
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=mess,
                                             random_id=random.randint(0, 2 ** 64))
                        except:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message='Неверный формат языка, введите !языки',
                                             random_id=random.randint(0, 2 ** 64))
                    elif text[:9] == 'будильник':
                        try:
                            text = list(map(int, text.split(' ')[1:]))
                            if len(text) == 3:
                                time = datetime.now()
                                ye = int(time.strftime("%Y"))
                                m = int(time.strftime("%m"))
                                ch = text[0]
                                h = text[1]
                                min = text[2]
                                data = datetime(ye, m, ch, h, min, 0)
                                if data < datetime.now():
                                    x = 0 / 0
                                else:
                                    delta = data - datetime.now()
                                    x = str(delta)
                                    if ', ' in x:
                                        x = x.split(', ')
                                        x[0] = x[0][:-5]
                                        days = x[0]
                                        x[1] = x[1].split(':')
                                        x[1][2] = x[1][2][:-7]
                                        x[1] = list(map(int, x[1]))
                                        hours = x[1][0]
                                        mins = x[1][1]
                                        sec = x[1][2]
                                        tex = 'Будильник сработает через '
                                        if days:
                                            tex += str(days) + ' дней, '
                                        if hours:
                                            tex += str(hours) + ' часов, '
                                        if mins:
                                            tex += str(mins) + ' минут, '
                                        tex += str(sec) + ' секунд.'
                                    else:
                                        x = x.split(':')
                                        x[2] = x[2][:-7]
                                        x = list(map(int, x))
                                        days = 0
                                        hours = x[0]
                                        mins = x[1]
                                        sec = x[2]
                                        tex = 'Будильник сработает через '
                                        if hours:
                                            tex += str(hours) + ' часов, '
                                        if mins:
                                            tex += str(mins) + ' минут, '
                                        tex += str(sec) + ' секунд.'

                                    vk.messages.send(user_id=event.obj.message['from_id'],
                                                     message=tex,
                                                     random_id=random.randint(0, 2 ** 64))
                            else:
                                time = datetime.now()
                                ye = int(time.strftime("%Y"))
                                m = int(time.strftime("%m"))
                                ch = int(time.strftime("%d"))
                                h = text[0]
                                min = text[1]
                                data = datetime(ye, m, ch, h, min, 0)
                                if data < datetime.now():
                                    x = 0 / 0
                                else:
                                    delta = data - datetime.now()
                                    x = str(delta)
                                    x = x.split(':')
                                    x[2] = x[2][:-7]
                                    x = list(map(int, x))
                                    days = 0
                                    hours = x[0]
                                    mins = x[1]
                                    sec = x[2]
                                    tex = 'Будильник сработает через '
                                    if hours:
                                        tex += str(hours) + ' часов, '
                                    if mins:
                                        tex += str(mins) + ' минут, '
                                    tex += str(sec) + ' секунд.'
                                    vk.messages.send(user_id=event.obj.message['from_id'],
                                                     message=tex,
                                                     random_id=random.randint(0, 2 ** 64))
                            many_seconds = days * 84600 + hours * 3600 + mins * 60 + sec + 1
                            Timer = threading.Timer(many_seconds, good_morning, args=[event.obj.message['from_id']])
                            Timer.start()
                        except:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message='Неверный формат даты',
                                             random_id=random.randint(0, 2 ** 64))
                    elif text[:9] == 'уравнение':
                        try:
                            text = text.split()
                            type = int(text[1])
                            args = list(map(float, text[2:]))
                            res = ''
                            if type == 1:
                                a = args[0]
                                b = args[1]
                                if a == 0 and b == 0:
                                    res = 'x ∈ R'
                                elif a == 0 and b != 0:
                                    res = 'Нет корней'
                                else:
                                    res = 'x = ' + str(-1 * b / a)
                            elif type == 2:
                                a = args[0]
                                b = args[1]
                                c = args[2]
                                d = b ** 2 - 4 * a * c
                                if d < 0:
                                    res = 'Нет действительный корней'
                                elif d == 0:
                                    x = -1 * b / (2 * a)
                                    res = 'x = ' + str(x)
                                else:
                                    x1 = (-1 * b + d ** 0.5) / (2 * a)
                                    x2 = (-1 * b - d ** 0.5) / (2 * a)
                                    res = 'x1 = ' + str(x1) + ', x2 = ' + str(x2)
                            else:
                                a = args[0]
                                b = args[1]
                                c = args[2]
                                d = args[3]
                                e = args[3]
                                f = args[3]
                                if a / d == b / e == c / f:
                                    res = 'Недостаточно данных'
                                else:
                                    x = (e * c - b * f) / (b * d - e * a)
                                    y = (-1 * a * x - c) / b
                                    res = 'x = ' + str(x) + ', y = ' + str(y)
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=res,
                                             random_id=random.randint(0, 2 ** 64))
                        except:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message='Ошибка данных',
                                             random_id=random.randint(0, 2 ** 64))
                    elif text[:11] == 'калькулятор':
                        try:
                            vir = text[12:]
                            vir = vir + ' = ' + str(eval(vir.replace('^', '**')))
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=vir.replace('  ', ' '),
                                             random_id=random.randint(0, 2 ** 64))
                        except:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message="Ошибка в выражении",
                                             random_id=random.randint(0, 2 ** 64))
                    else:
                        qwerty = 0 / 0
                except:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Вы ввели неверную команду, для получения списка команд введите !команды",
                                     random_id=random.randint(0, 2 ** 64))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Здравствуйте! Я - бот, со списком команд можно ознакомиться, введя !команды",
                                 random_id=random.randint(0, 2 ** 64))

        if event.type == VkBotEventType.GROUP_JOIN:
            vk = vk_session.get_api()
            vk.messages.send(user_id=event.obj.user_id,
                             message="Спасибо за вступление в группу!",
                             random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
