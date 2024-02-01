from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.

class AzurePricing(models.Model):
    sku = models.CharField(max_length=100)
    retail_price = models.FloatField()
    unit_of_measure = models.CharField(max_length=50)
    region = models.CharField(max_length=100)
    meter = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.sku} - {self.product_name}"

# class Restaurant(models.Model):
#     name = models.CharField(max_length=50)
#     street_address = models.CharField(max_length=50)
#     description = models.CharField(max_length=250)

#     def __str__(self):
#         return self.name


# class Review(models.Model):
#     restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
#     user_name = models.CharField(max_length=20)
#     rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
#     review_text = models.CharField(max_length=500)
#     review_date = models.DateTimeField('review date')

#     def __str__(self):
#         return f"{self.restaurant.name} ({self.review_date:%x})"