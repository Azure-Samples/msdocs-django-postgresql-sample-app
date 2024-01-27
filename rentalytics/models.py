from django.db import models

# Create your models here.
class Country(models.Model):
    # Automatic id field added by Django: id (AutoField)
    country_code = models.CharField(max_length=3)  # Assuming country codes are 3 letters
    country_name = models.CharField(max_length=100)

    def __str__(self):
        return self.country_name

class Province(models.Model):
    # Automatic id field added by Django: id (AutoField)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    province_name = models.CharField(max_length=100)

    def __str__(self):
        return self.province_name

class City(models.Model):
    # Automatic id field added by Django: id (AutoField)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return self.city_name

class District(models.Model):
    # Automatic id field added by Django: id (AutoField)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    district_name = models.CharField(max_length=100)

    def __str__(self):
        return self.district_name