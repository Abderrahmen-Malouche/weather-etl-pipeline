import requests
import os

api_key=os.getenv("API_KEY")
destination="New York"
api_url=f"http://api.weatherstack.com/current?access_key={api_key}&query={destination}"

def fetch_data():
    print("Fetching weather Data from weatherstack API...")
    try:
        response=requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")

fetch_data()

def mock_fetch_data():
    return {
        "request": {
            "type": "City",
            "query": "New York, United States of America",
            "language": "en",
            "unit": "m"
        },
        "location": {
            "name": "New York",
            "country": "United States of America",
            "region": "New York",
            "lat": "40.714",
            "lon": "-74.006",
            "timezone_id": "America/New_York",
            "localtime": "2024-06-15 10:00",
            "localtime_epoch": 1718361600,
            "utc_offset": "-4.0"
        },
        "current": {
            "observation_time": "02:00 PM",
            "temperature": 25,
            "weather_code": 113,
            "weather_icons": [
                "https://assets.weatherstack.com/images/wsymbols01_png_64/wsymbol_0001_sunny.png"
            ],
            "weather_descriptions": [
                "Sunny"
            ],
            "wind_speed": 10,
            "wind_degree": 230,
            "wind_dir": "SW",
            "pressure": 1015,
            "precip": 0,
            "humidity": 60,
            "cloudcover": 0,
            "feelslike": 27,
            "uv_index": 7,
            "visibility": 16
        }
    }