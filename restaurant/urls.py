from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('menu/', views.menu, name='menu'),  # Menu page
    # Add more paths as needed
]
