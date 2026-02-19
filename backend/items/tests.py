from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Item


class ItemModelTest(TestCase):
    def test_create_item(self):
        item = Item.objects.create(name='Test Item', description='Test description')
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.description, 'Test description')
        self.assertIsNotNone(item.created_at)
        self.assertEqual(str(item), 'Test Item')


class ItemAPITest(APITestCase):
    def setUp(self):
        self.item = Item.objects.create(name='Item 1', description='Desc 1')
        self.list_url = reverse('item-list')

    def detail_url(self, pk):
        return reverse('item-detail', args=[pk])

    def test_list_items(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_item(self):
        data = {'name': 'New Item', 'description': 'New description'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Item')

    def test_retrieve_item(self):
        response = self.client.get(self.detail_url(self.item.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Item 1')

    def test_update_item(self):
        data = {'name': 'Updated', 'description': 'Updated desc'}
        response = self.client.put(self.detail_url(self.item.pk), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated')

    def test_delete_item(self):
        response = self.client.delete(self.detail_url(self.item.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.count(), 0)
