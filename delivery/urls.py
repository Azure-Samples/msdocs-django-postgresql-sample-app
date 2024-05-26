from django.urls import path

from .views import (
    address_autocomplete,
    address_autocomplete_view,
    form_view,
    handle_form,
    redirect_page_view,
)

urlpatterns = [
    path("autocomplete/", address_autocomplete, name="address_autocomplete"),
    path(
        "address-autocomplete/",
        address_autocomplete_view,
        name="address_autocomplete_view",
    ),
    path("redirect-page/", redirect_page_view, name="redirect_page_view"),
    path("form/", form_view, name="form_view"),
    path("handle-form/", handle_form, name="handle_form"),
]
