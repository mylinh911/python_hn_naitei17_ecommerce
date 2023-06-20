from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import Customer

class CustomerAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('register-api')

    def test_create_customer_with_valid_data(self):
        data = {
            'user_name': 'john_doe',
            'password': 'password123',
            'email': 'john@example.com',
            'full_name': 'John Doe',
            'address': '123 Main St',
            'phone': '1234567890',
        }

        initial_count = Customer.objects.count()  

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), initial_count + 1)  
        self.assertEqual(Customer.objects.get().user_name, 'john_doe')

    def test_create_customer_with_duplicate_user_name(self):
        # Create a customer with the same user_name
        Customer.objects.create(
            user_name='john_doe',
            password='password123',
            email='john@example.com',
            full_name='John Doe',
            address='123 Main St',
            phone='1234567890',
        )

        data = {
            'user_name': 'john_doe',
            'password': 'password456',
            'email': 'john456@example.com',
            'full_name': 'John Doe 456',
            'address': '456 Main St',
            'phone': '0987654321',
        }

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['user_name'][0]), "{'This user_name already exists.'}")
        self.assertEqual(Customer.objects.count(), 1)
