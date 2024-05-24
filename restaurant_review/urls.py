from django.urls import path

from .views import (
    address_autocomplete_view,
    autocomplete_address,
    redirect_page_view,
)

urlpatterns = [
    path("autocomplete/", autocomplete_address, name="autocomplete_address"),
    path(
        "address-autocomplete/",
        address_autocomplete_view,
        name="address_autocomplete_view",
    ),
    path("redirect-page/", redirect_page_view, name="redirect_page_view"),
]
