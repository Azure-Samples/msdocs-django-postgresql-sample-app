# fetch_azure_data.py

import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azureproject.settings')
django.setup()

from restaurant_review.models import AzurePricing

def fetch_all_data_and_save(api_url):
    response = requests.get(api_url)
    data = json.loads(response.text)
    
    for item in data['Items']:
        AzurePricing.objects.create(
            sku=item['armSkuName'],
            retail_price=item['retailPrice'],
            unit_of_measure=item['unitOfMeasure'],
            region=item['armRegionName'],
            meter=item['meterName'],
            product_name=item['productName']
        )

        if 'NextPageLink' in data:
            fetch_all_data_and_save(data['NextPageLink'])

api_url = "https://prices.azure.com/api/retail/prices?%24filter=contains(armSkuName, 'Standard_A1_v2')"
fetch_all_data_and_save(api_url)
