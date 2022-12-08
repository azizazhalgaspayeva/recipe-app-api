"""
Tests for the ingredients API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@example.com', password='test123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(
        email=email,
        password=password,
    )


def detail_url(ingredient_id):
    """Return reverse of particular ingredient url address."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsAPITests(TestCase):
    """Tests for unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingridients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Tests for authenticated API requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieve ingredients."""
        Ingredient.objects.create(
            user=self.user,
            name='Milk',
        )
        Ingredient.objects.create(
            user = self.user,
            name='Sugar',
        )
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test update ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Carlic',
        )

        payload = {'name': 'Garlic'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test delete ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Garlic',
        )

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ingredients.exists())