import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


def address_autocomplete_view(request):
    print("is here")
    return render(request, "address_autocomplete.html")


def redirect_page_view(request):
    address = request.GET.get("selected_address")
    if not address:
        return JsonResponse({"error": "No address provided"}, status=400)

    access_token = settings.MAPBOX_ACCESS_TOKEN
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {"access_token": access_token, "country": "CL"}

    response = requests.get(url, params=params)
    data = response.json()
    origin = data.get("features")[0].get("center")
    print(origin)
    # google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin[1]},{origin[0]}"
    # print(google_maps_url)

    if response.status_code != 200 or not data["features"]:
        return JsonResponse(
            {"error": "Address not found or invalid request"}, status=404
        )
    return render(request, "entrepreneur_selection.html")


def autocomplete_address(request):
    query = request.GET.get("query", None)
    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)

    access_token = settings.MAPBOX_ACCESS_TOKEN
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    params = {
        "access_token": access_token,
        "autocomplete": "true",
        "country": "CL",
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        return JsonResponse(
            {"error": "Error fetching data from Mapbox"},
            status=response.status_code,
        )

    suggestions = [
        {
            "place_name": feature["place_name"],
            "bbox": feature.get("bbox", []),
            "center": feature["center"],
        }
        for feature in data["features"]
    ]

    return JsonResponse({"suggestions": suggestions})
