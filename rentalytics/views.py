from django.shortcuts import render, redirect
from .models import Country
from .forms import CountryForm


# Create your views here.
def home(request):
    # Fetch all countries with their related provinces
    countries = Country.objects.prefetch_related('province_set').all()
    return render(request, 'home.html', {'countries': countries})

def add_country(request):
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the home page or wherever appropriate
    else:
        form = CountryForm()

    return render(request, 'add_country.html', {'form': form})