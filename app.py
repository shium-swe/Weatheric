from flask import Flask, render_template, request
import requests, json, os
from dotenv import load_dotenv

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/forecast", methods=["POST"])
def forecast():
  city = request.form.get("city", "boston")

  def configure():
    load_dotenv()

  def main():
    configure()
    city_name = city
    API_KEY = os.getenv('api_key')
    info = getLonLat(API_KEY, city_name)
    weather_data = getForecastData(API_KEY, info)
    weather_forecast = createWeatherObjs(weather_data, city_name)
    return weather_forecast

  def getLonLat(API_KEY, city_name):
    URL = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}'
    response = requests.get(URL)

    if response.status_code == 200: # makes sure that the response is OK
      data = response.json()

    lon = data['coord']['lon'] 
    lat = data['coord']['lat']

    coord_info = [] # using a list data abstraction to store this data
    coord_info.append(lon)
    coord_info.append(lat)

    return coord_info # return this list for other functions to use

  def getForecastData(API_KEY, info):
    lon = info[0]
    lat = info[1]
    exclude = 'minute,hourly' # Excluding data I dont need from API call

    URL2 = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid={API_KEY}'
    response2 = requests.get(URL2)
    data2 = response2.json()

    days = [] # storing select few data points in JSON in there own lists
    nights = []
    desc = []

    for i in data2['daily']:
      # Temperature data
      days.append(str(round((i['temp']['day'] - 273.15 ) * 1.8 + 32, 1))) # adding temperature data that is converted into Fahrenheit and rounded
      nights.append(str(round((i['temp']['night'] - 273.15 ) * 1.8 + 32, 1)))

      # Weather conditions
      desc.append(i['weather'][0]['description'])

    week_data = []
    week_data.append(days)
    week_data.append(desc)
    week_data.append(nights)

    return week_data # this is a nested list of all data needed

  def createWeatherObjs(weather_data, city_name):
    days_temp = weather_data[0]
    nights_temp = weather_data[1]
    daily_desc = weather_data[2]
    numOfObjects = len(weather_data[0])

    weather_objs = list(zip(days_temp, nights_temp, daily_desc)) # zip function ties all the data from the list based on the index and list converts tuple into list
    
    # creating my weather forecast object
    # this object bundles all the information and useful methods together
    weather_forecast = WeatherInfo(weather_objs[0], weather_objs[1], weather_objs[2], weather_objs[3], weather_objs[4], weather_objs[5], weather_objs[6], weather_objs[7], city_name, weather_objs) # passing in indexing nested list and passing it in the object as arguments
    return weather_forecast 

  data = main()
  return render_template("forecast.html", city=data)


class WeatherInfo:
  def __init__(self, weather_0, weather_1, weather_2, weather_3, weather_4, weather_5, weather_6, weather_7, city_name, all_weather):
    self.weather_0 = weather_0
    self.weather_1 = weather_1
    self.weather_2 = weather_2
    self.weather_3 = weather_3
    self.weather_4 = weather_4
    self.weather_5 = weather_5
    self.weather_6 = weather_6
    self.weather_7 = weather_7
    self.city_name = city_name
    self.all_weather = all_weather

  def getTodaysWeather(self): # Gives today's weather forecast using the the weather_1 instance variable which is a list
    return f"The weather in {self.city_name} today is {self.weather_0[0]} degrees during the day and {self.weather_0[2]} degrees during the night. {self.city_name} is going to get some {self.weather_0[1]}."

  def getTomorrowsWeather(self): # Gives tomorrow's weather forecast using the the weather_2 instance variable which is a list
    return f"The weather tomorrow in {self.city_name} is {self.weather_1[0]} degrees during the day and {self.weather_1[2]} degrees during the night. {self.city_name} is going to get some {self.weather_1[1]}."

  def getHottestTemp(self):
    hottest_day = max(self.all_weather, key=lambda x: x[0]) # using lambda expression to get the hottest temperature in the nested list. Knowing that the hottest temperature in the day is during the day, I use the right key
    hottest_temp = str(hottest_day[0]) # indexing the useful data from list
    return f"The hottest temperature in the next 7 days in {self.city_name} is {hottest_temp} degrees!" 

  def getColdestTemp(self):
    coldest_day = min(self.all_weather, key=lambda x: x[2])
    coldest_temp = str(coldest_day[0])
    return f"The coldest temperature in the next 7 days in {self.city_name} is {coldest_temp} degrees!" # same with getHottestTemp except I use the night so I change the key