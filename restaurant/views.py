from django.shortcuts import render
from restaurant.models import MenuItem, MenuSection

# Create your views here.

def home(request):
    return render(request, 'restaurant/home.html')  # Render the home page

def menu(request):
    # Fetch all active menu sections
    sections = MenuSection.objects.filter(is_active=True)

    # For each section, fetch associated active menu items
    menu_data = []
    for section in sections:
        items = MenuItem.objects.filter(section=section, is_active=True)
        menu_data.append({
            'section': section,
            'items': items
        })

    # Pass the menu data to the template
    context = {'menu_data': menu_data}
    return render(request, 'restaurant/menu.html', context)