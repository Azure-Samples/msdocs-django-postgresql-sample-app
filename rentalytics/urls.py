from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-country/', views.add_country, name='add_country'),
]
