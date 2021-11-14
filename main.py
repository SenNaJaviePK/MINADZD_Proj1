import requests
import json
from datetime import datetime, timedelta
import time

api_key = '3b3b2ba819d8c7377a392492d3b2151b'


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

    coordinated_weather = TimestampLocalizationWeather(
        json_weather["name"],
        json_weather["sys"]["country"],
        datetime.fromtimestamp(json_weather["dt"]),
        json_weather["coord"]["lon"],
        json_weather["coord"]["lat"],
        collected_weather,
    )

    return coordinated_weather


def parse_historical_weather_api_data(historical_weather_data):
    json_weather = json.loads(historical_weather_data)
    hourly_stats = []

    for hour in json_weather["hourly"]:
        collected_weather = Weather(
            hour["temp"],
            hour["temp"],
            hour["temp"],
            hour["temp"],
            hour["pressure"],
            hour["humidity"],
            hour["visibility"],
            hour["wind_speed"],
            hour["clouds"],
        )

        hourly_stats.append(collected_weather)

    #return reversed array
    return hourly_stats[::-1]


def GatherCurrentWeatherData(city_search_values):
    for city in city_search_values:
        request_time = datetime.now()

        request_time_stamp = time.mktime(request_time.timetuple())
        request = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&dt={request_time_stamp}'

        code, weather_data = collect_weather_data(request)
        if code == 200:
            parsed_weather_data = parse_weather_api_data(weather_data)

            #print(parsed_weather_data.city, parsed_weather_data.country_code, parsed_weather_data.weather.temp, parsed_weather_data.timestamp)

            yield parsed_weather_data


def GatherHistoricalWeatherData(lat, lon, max_hours_back):
    # Open api allows max 5 days back in free sub
    if max_hours_back > 5 * 24:
        max_hours_back = 5 * 24
    elif max_hours_back < 0:
        max_hours_back = 0

    days_ago = 0
    hours_to_gather = max_hours_back

    while hours_to_gather > 0:
        request_time = datetime.now() - timedelta(hours=days_ago * 24)
        request_time_stamp = int(time.mktime(request_time.timetuple()))

        request = f'https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}' \
                  f'&dt={request_time_stamp}&appid={api_key}&units=metric'

        code, weather_data = collect_weather_data(request)

        if code == 200:
            parsed_weather_data = parse_historical_weather_api_data(weather_data)

            for i in range(len(parsed_weather_data)):
                #print(parsed_weather_data[i].temp)
                yield parsed_weather_data[i]
                hours_to_gather -= 1
                if hours_to_gather == 0:
                    break;


        days_ago += 1


def main():
    city_search_values = ["Krakow, PL", "Warszawa, PL", "Poznan, PL", "Katowice, PL", "Wroclaw, PL",
                      "Gdansk, PL", "Szczecin, PL", "Lodz, PL", "Rzeszow, PL", "Bialystok, PL"]

    max_hours_back = 5

    for result in GatherCurrentWeatherData(city_search_values):
        print(result.city, result.country_code, result.weather.temp,
              result.timestamp)

        print("Historical data:")
        i = 1
        for historical_temp in GatherHistoricalWeatherData(lat=result.lat, lon=result.lon, max_hours_back=max_hours_back):
            print(f"{i} hours ago: temp = {historical_temp.temp}")
            i += 1


if __name__ == '__main__':
    main()

