import asyncio
import datetime
import json

import requests
from bs4 import BeautifulSoup as bs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Weather
from storage.storage import get_async_session, async_session_maker

moscow_timezone = datetime.timezone(datetime.timedelta(hours=3))
lipetsk = "weather-lipetsk-4437"
yelets = "weather-yelets-4436"


def send_request(url, headers, params):
    return requests.get(url, headers=headers, params=params).text


def get_gismetio_data_now(city: str, service_id, city_id):
    print("now")

    headers = {
        'authority': 'www.gismeteo.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        # 'cookie': 'ab_audience_2=57; cityIP=4437; _ym_uid=1701292983244998305; _ym_d=1701292983; _gid=GA1.2.2132082929.1706879510; _ga_JQ0KX9JMHV=GS1.1.1706879510.7.0.1706879510.60.0.0; _ga=GA1.1.1403811258.1701292983; _ym_isad=1; _ym_visorc=b',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    url = f"https://www.gismeteo.ru/{city}/now/"
    response = send_request(url, headers, None)
    soup = bs(response, "html.parser")
    temp_now_wrap = soup.find("div", class_="weather-value")

    desc_now = soup.find("div", class_="now-desc").get_text()
    print("desc")
    print(desc_now)

    temp_now = convert_value_temp_to_int(temp_now_wrap.find("span").getText())

    print("temp")
    print(temp_now)

    wind_now_wrap = soup.find("div", class_="now-info-item wind").find("div", class_="item-value")
    wind_now_value_direction = wind_now_wrap.find("div", class_="unit unit_wind_m_s").get_text().split("м/c")
    wind_now_value = int(wind_now_value_direction[0])
    wind_now_direction = wind_now_value_direction[1]
    print("wind")
    print(wind_now_value)
    if len(wind_now_direction) > 3:
        wind_now_direction = convert_wind_direction(wind_now_direction)

    pressure_now_value = int(soup.find("div", class_="now-info-item pressure").
                             find("div", class_="unit unit_pressure_mm_hg").
                             get_text().replace("ммрт. ст.", ""))
    print("pressure")
    print(pressure_now_value)

    humidity_now_value = int(soup.find("div", class_="now-info-item humidity").
                             find("div", class_="item-value").get_text())
    print("humidity")
    print(humidity_now_value)
    weather = Weather()

    weather.date = datetime.datetime.now()
    weather.service_id = service_id
    weather.city_id = city_id
    weather.description = desc_now
    weather.temperature = temp_now
    weather.wind_value = wind_now_value
    weather.wind_direction = wind_now_direction
    weather.pressure = pressure_now_value
    weather.humidity = humidity_now_value
    weather.type = "now"
    return weather


def get_gismetio_data_today(city, service_id, city_id):
    print("today")

    headers = {
        'authority': 'www.gismeteo.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'cookie': 'ab_audience_2=57; cityIP=4437; _ym_uid=1701292983244998305; _ym_d=1701292983; _gid=GA1.2.2132082929.1706879510; _ym_isad=1; _ym_visorc=b; _gat=1; _ga_JQ0KX9JMHV=GS1.1.1706883743.8.1.1706890602.58.0.0; _ga=GA1.1.1403811258.1701292983',
        'referer': 'https://www.gismeteo.ru/weather-lipetsk-4437/tomorrow/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    url = f"https://www.gismeteo.ru/{city}"
    response = send_request(url, headers, None)
    soup = bs(response, "html.parser")

    descs = soup.find("div", attrs={"data-row": "icon-tooltip"}).find_all("div", class_="row-item")
    descs_values = [desc.find("div").get("data-text")
                    for desc in descs]
    # print(descs_values)

    temps = soup.find("div", class_="widget-row-chart widget-row-chart-temperature row-with-caption",
                      attrs={"data-row": "temperature-air"}).find_all("div", class_="value")
    temps_values = [convert_value_temp_to_int(temp.find("span").get_text()) for temp in temps]
    # print(temps_values)

    winds = soup.find("div", attrs={"data-row": "wind-speed"}).find_all("div", class_="row-item")
    winds_values = [int(wind.find("span", class_="wind-unit unit unit_wind_m_s").get_text()) for wind in winds]
    # print(winds_values)

    winds = soup.find("div", attrs={"data-row": "wind-direction"}).find_all("div", class_="row-item")
    winds_direction = [wind.find("div", class_="direction").get_text() for wind in winds]
    # print(winds_direction)

    pressures = soup.find("div", attrs={"data-row": "pressure"}).find_all("div", class_="value")
    pressures_values = [int(pressure.find("span", class_="unit unit_pressure_mm_hg").get_text()) for pressure in
                        pressures]
    # print(pressures_values)

    humidity = soup.find("div", attrs={"data-row": "humidity"}).find_all("div")
    humidity_values = [int(h.get_text()) for h in humidity]
    # print(humidity_values)

    date_now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    dates = [(date_now + datetime.timedelta(hours=i * 3)) for i in range(8)]
    weathers = []
    for i in range(8):
        weather = Weather()

        weather.date = dates[i]
        weather.service_id = service_id
        weather.city_id = city_id
        weather.description = str(descs_values[i])
        weather.temperature = temps_values[i]
        weather.wind_value = winds_values[i]
        weather.wind_direction = winds_direction[i]
        weather.pressure = pressures_values[i]
        weather.humidity = humidity_values[i]
        weather.type = "today"
        weathers.append(
            weather
        )
    return weathers


def get_gismetio_data_10_days(city, service_id, city_id):
    print("10 days")

    headers = {
        'authority': 'www.gismeteo.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        # 'cookie': 'ab_audience_2=57; cityIP=4437; _ym_uid=1701292983244998305; _ym_d=1701292983; _gid=GA1.2.2132082929.1706879510; _ym_isad=1; _ym_visorc=b; _gat=1; _ga_JQ0KX9JMHV=GS1.1.1706905950.10.1.1706908459.59.0.0; _ga=GA1.1.1403811258.1701292983',
        'referer': 'https://www.gismeteo.ru/weather-lipetsk-4437/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    url = f"https://www.gismeteo.ru/{city}/10-days/"
    response = send_request(url, headers, None)
    soup = bs(response, "html.parser")

    descs = soup.find("div", attrs={"data-row": "icon-tooltip"}).find_all("div", class_="row-item")
    descs_values = [desc.find("div").get("data-text")
                    for desc in descs]
    # print(descs_values)

    temps = soup.find("div", attrs={"data-row": "temperature-avg"}).find_all("div", class_="value")
    temps_values = [convert_value_temp_to_int(temp.find("span", class_="unit unit_temperature_c").get_text())
                    for temp in temps]
    # print(temps_values)

    winds = soup.find("div", attrs={"data-row": "wind-speed"}).find_all("div", class_="row-item")
    winds_values = [int(wind.find("span", class_="wind-unit unit unit_wind_m_s").get_text()) for wind in winds]
    # print(winds_values)

    winds = soup.find("div", attrs={"data-row": "wind-direction"}).find_all("div", class_="row-item")
    winds_direction = [wind.find("div", class_="direction").get_text() for wind in winds]
    # print(winds_direction)

    pressures = soup.find("div", attrs={"data-row": "pressure"}).find_all("div", class_="value")
    pressures_values = [(int(pressure.find("div", class_="maxt").find("span",
                                                                      class_="unit unit_pressure_mm_hg").get_text()) + int(
        pressure.find("div", class_="mint").find("span", class_="unit unit_pressure_mm_hg").get_text())) // 2 for
                        pressure in
                        pressures]
    # print(pressures_values)

    humidity = soup.find("div", attrs={"data-row": "humidity"}).find_all("div")
    humidity_values = [int(h.get_text()) for h in humidity]
    # print(humidity_values)

    date_now = datetime.date.today()

    dates = [(date_now + datetime.timedelta(days=i)) for i in range(10)]
    weathers = []
    for i in range(10):
        weather = Weather()

        weather.date = dates[i]
        weather.service_id = service_id
        weather.city_id = city_id
        weather.description = str(descs_values[i])
        weather.temperature = temps_values[i]
        weather.wind_value = winds_values[i]
        weather.wind_direction = winds_direction[i]
        weather.pressure = pressures_values[i]
        weather.humidity = humidity_values[i]
        weather.type = "days"
        weathers.append(
            weather
        )
    return weathers


def convert_value_temp_to_int(temp: str):
    if temp[0] == '+':
        return int(temp)
    elif not temp[0].isdigit():
        return int('-' + temp[1:])
    return int(temp)


def convert_wind_direction(direction: str) -> str:
    data = {
        "северный": "С",
        "северо-западный": "С/З",
        "северо-восточный": "С/В",
        "восточный": "В",
        "западный": "З",
        "южный": "Ю",
        "южно-восточный": "Ю/В",
        "южно-западный": "Ю/З",
    }
    return data[direction]


async def gismetio_lipetsk_now():
    weather = get_gismetio_data_now(lipetsk, 1, 1)
    await save_weather(weather)


async def gismetio_lipetsk_today():
    weathers = get_gismetio_data_today(lipetsk, 1, 1)
    for weather in weathers:
        await save_weather(weather)


async def gismetio_lipetsk_days():
    weathers = get_gismetio_data_10_days(lipetsk, 1, 1)
    for weather in weathers:
        await save_weather(weather)


async def save_weather(weather):
    async with async_session_maker() as session:
        session: AsyncSession
        session.add(weather)
        # await session.execute(text("delete from weather where weather.type='now'"))
        await session.commit()


# async def test_weather():
#     async with async_session_maker() as session:
#
#         result = await session.execute(text("select * from weather order by weather_id desc limit 1"))
#         for row in result:
#             print(row)

async def main():
    pass
    # await asyncio.gather(asyncio.create_task(gismetio_lipetsk_now()),
    #                      asyncio.create_task(gismetio_lipetsk_today())
    #                      )
    await asyncio.gather(asyncio.create_task(gismetio_lipetsk_days()))


if __name__ == "__main__":
    # get_gismetio_data_10_days(lipetsk, 1, 1)

    asyncio.run(main())
    # get_gismetio_data_today(lipetsk, 1, 1)
    # asyncio.run(test_weather())
