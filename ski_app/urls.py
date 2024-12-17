from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_weather, name='search_weather'),
]