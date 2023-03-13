import datetime

from django.test import TestCase
from django.urls import reverse

from .models import Restaurant


def create_restaurant():
    return Restaurant.objects.create(
        name="Test Restaurant",
        street_address="123 Test Street",
        description="Test Description",
    )


# Initial tests created with GitHub Copilot
class RestaurantRoutesTestCase(TestCase):
    def test_restaurant_review_page_loads(self):
        restaurant = create_restaurant()
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, restaurant.name)

    def test_restaurant_details_page_loads(self):
        restaurant = create_restaurant()
        response = self.client.get(reverse("details", args=(restaurant.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, restaurant.name)

    def test_create_restaurant_page_loads(self):
        response = self.client.get(reverse("create_restaurant"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Restaurant")

    def test_add_restaurant(self):
        response = self.client.post(
            reverse("add_restaurant"),
            {
                "restaurant_name": "Test Restaurant",
                "street_address": "123 Test Street",
                "description": "Test Description",
            },
        )
        restaurant = Restaurant.objects.get(name="Test Restaurant")
        self.assertEqual(restaurant.name, "Test Restaurant")
        self.assertEqual(restaurant.street_address, "123 Test Street")
        self.assertEqual(restaurant.description, "Test Description")
        self.assertRedirects(response, reverse("details", args=(restaurant.id,)))

    def test_add_review(self):
        restaurant = create_restaurant()
        response = self.client.post(
            reverse("add_review", args=(restaurant.id,)),
            {"user_name": "Test User", "rating": 5, "review_text": "Test Review"},
        )
        self.assertEqual(restaurant.review_set.count(), 1)
        review = restaurant.review_set.first()
        self.assertEqual(review.user_name, "Test User")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, "Test Review")
        self.assertRedirects(response, reverse("details", args=(restaurant.id,)))


class RestaurantModels(TestCase):
    def test_create_restaurant(self):
        restaurant = create_restaurant()
        self.assertEqual(restaurant.name, "Test Restaurant")
        self.assertEqual(restaurant.street_address, "123 Test Street")
        self.assertEqual(restaurant.description, "Test Description")
        self.assertEqual(str(restaurant), "Test Restaurant")

    def test_create_review(self):
        restaurant = create_restaurant()
        review = restaurant.review_set.create(
            user_name="Test User",
            rating=5,
            review_text="Test Review",
            review_date=datetime.datetime(2001, 1, 1),
        )
        self.assertEqual(review.user_name, "Test User")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, "Test Review")
        self.assertEqual(str(review), "Test Restaurant (01/01/01)")
