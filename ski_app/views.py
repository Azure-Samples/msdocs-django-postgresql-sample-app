from django.shortcuts import render
from django.http import HttpResponse
import requests

def search_weather(request):
    city = request.GET.get('city')
    error = None
    weather = None

    if city:
        try:
            # Fetch latitude and longitude
            headers = {"User-Agent": "SkiApp"}
            nominatim_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
            nom_response = requests.get(nominatim_url, headers=headers)
            nom_response.raise_for_status()
            location = nom_response.json()[0]
            lat, lon = location['lat'], location['lon']

            # Fetch weather data
            weather_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": ["temperature_2m", "snowfall", "snow_depth", "weather_code", "cloud_cover"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "sunshine_duration"],
                "current": ["temperature_2m","snow_depth","snowfall","weather_code"],
                "timezone": "Europe/Berlin"
            }
            weather_response = requests.get(weather_url, params=params)
            weather_response.raise_for_status()
            weather = weather_response.json()
            weather['latitude'] = lat
            weather['longitude'] = lon
        except Exception as e:
            error = f"{e} City not found or an error occurred. Please try again."

    return render(request, "search_results.html", {"city": city, "weather": weather, "error": error})
