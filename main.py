import requests
import json
from datetime import datetime

api_key = '3b3b2ba819d8c7377a392492d3b2151b'

city_search_values = ["Krakow, PL", "Warszawa, PL", "Poznan, PL", "Katowice, PL", "Wroclaw, PL",
                      "Gdansk, PL", "Szczecin, PL", "Lodz, PL", "Rzeszow, PL", "Bialystok, PL"]


class Weather:
    def __init__(self, min_temp, max_temp, temp, feels_like, pressure, humidity, visibility, wind_speed, clouds):
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.temp = temp
        self.feels_like = feels_like
        self.pressure = pressure
        self.humidity = humidity
        self.visibility = visibility
        self.wind_speed = wind_speed
        self.clouds = clouds


class TimestampLocalizationWeather:
    def __init__(self, city, country_code, timestamp, lon, lat, weather):
        self.city = city
        self.country_code = country_code
        self.timestamp = timestamp
        self.lon = lon
        self.lat = lat
        self.weather = weather


def collect_weather_data(request):
    weather_api_response = requests.get(request)

    response_code = weather_api_response.status_code
    response_data = weather_api_response.text

    return response_code, response_data


def parse_weather_api_data(weather_data):
    json_weather = json.loads(weather_data)

    collected_weather = Weather(
        json_weather["main"]["temp_min"],
        json_weather["main"]["temp_max"],
        json_weather["main"]["temp"],
        json_weather["main"]["feels_like"],
        json_weather["main"]["pressure"],
        json_weather["main"]["humidity"],
        json_weather["visibility"],
        json_weather["wind"]["speed"],
        json_weather["clouds"]["all"],
    )

    coodrinated_weather = TimestampLocalizationWeather(
        json_weather["name"],
        json_weather["sys"]["country"],
        datetime.now(),
        json_weather["coord"]["lon"],
        json_weather["coord"]["lat"],
        collected_weather,
    )

    return coodrinated_weather


for city in city_search_values:
    request = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    code, weather_data = collect_weather_data(request)
    if code == 200:
        parsed_weather_data = parse_weather_api_data(weather_data)

        print(parsed_weather_data.city, parsed_weather_data.country_code, parsed_weather_data.weather.temp, parsed_weather_data.timestamp)

