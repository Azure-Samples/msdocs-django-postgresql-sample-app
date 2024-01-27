from django import forms
from .models import Country

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['country_code', 'country_name']