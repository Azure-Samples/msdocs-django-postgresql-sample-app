import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render


def address_autocomplete_view(request):
    print("is here")
    return render(request, "address_autocomplete.html")


def redirect_page_view(request):
    address = request.GET.get("selected_address")


def address_autocomplete(request):
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


def form_view(request):
    return render(request, "address_form.html")


def handle_form(request):
    if request.method == "POST":
        address1 = request.POST.get("selected_address1")
        address2 = request.POST.get("selected_address2")
        date = request.POST.get("date")
        time = request.POST.get("time")
        access_token = settings.MAPBOX_ACCESS_TOKEN
        params = {"access_token": access_token, "country": "CL"}

        origin_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address1}.json"
        destination_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address2}.json"
        origin_response = requests.get(origin_url, params=params)
        destination_response = requests.get(destination_url, params=params)
        origin = origin_response.json().get("features")[0].get("center")
        destination = (
            destination_response.json().get("features")[0].get("center")
        )
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin[1]},{origin[0]}&destination={destination[1]},{destination[0]}&travelmode=driving"
        if (
            origin_response.status_code != 200
            or not origin_response.json().get("features")
            or destination_response.status_code != 200
            or not destination_response.json().get("features")
        ):
            return JsonResponse(
                {"error": "Address not found or invalid request"}, status=404
            )
        return render(request, "entrepreneur_selection.html")
    return redirect("form_view")
