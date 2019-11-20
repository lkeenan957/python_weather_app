import json
import requests
import pprint
import pymongo

CONFIG_FILE = 'config.json'
api_url_base = 'http://api.openweathermap.org/data/2.5/'

def get_weather(location):
    api_token = config["openweathermap"]["apikey"]
    api_url = '{0}weather?q={1}&appid={2}&units=imperial'.format(
        api_url_base, location, api_token
    )

    response = requests.get(api_url)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return response.content

def getdata():
    with open(CONFIG_FILE) as json_file:
        config = json.load(json_file)
    mclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = mclient["weatherDB"]
    
    collection = db["weatherDetails"]
    
    cursor = collection.find() 
    print("Getting data from the database")
    for record in cursor: 
        print('\n{0} weather: \n {1}, wind speed of {2} mph in the direction of {3} degrees\n Tempertature: {4}F, Humidity: {5}F \n'.format(
            record["name"],
            record["weather"][0]["description"],
            record["wind"]["speed"],
            record["wind"]["deg"],
            record["main"]["temp"],
            record["main"]["humidity"]
        ))

if __name__ == "__main__":

    with open('config.json') as json_file:
        config = json.load(json_file)

    mclient = pymongo.MongoClient("mongodb://localhost:27017/")
    
    db = mclient["weatherDB"]

    collection = db["weatherDetails"]

    
    for location in config['openweathermap']['locations']:
        print("Getting data from openweathermap")
        info = get_weather(location)
        data = {}
        data['name'] = location
        data['weather'] = info.get('weather')
        data['rain'] = info.get('rain')
        data['clouds'] = info.get('clouds')
        data['wind'] = info.get('wind')
        data['main'] = info.get('main')
        collection.find_one_and_update(
            {'name': location},
            {"$set": data},
            upsert=True
        )
    getdata()
