from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Customer, Order, Product, OrderDetail

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.home_url = reverse('home')
        self.logout_url = reverse('logout')
        self.product_list_url = reverse('products')
        self.cart_url = reverse('cart')
        self.checkout_url = reverse('checkout')
        self.order_list_url = reverse('orderlist')
        self.product = Product.objects.create(name='Test Product', price=10.99)  
        self.detail_url = reverse('product-detail', args=[self.product.pk])

    def test_register_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_home_view(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  

    def test_product_list_view(self):
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, 200)

    def test_cart_view(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_checkout_view(self):
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)

    def test_order_list_view(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, 200)

    def test_order_detail_view(self):
        order = Order.objects.create(customer=Customer.objects.create(), status='demo')
        order_detail_url = reverse('order-detail', kwargs={'pk': order.pk})

        response = self.client.get(order_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        customer = Customer.objects.create(full_name='John Doe', userID=1000)

        session = self.client.session
        session['john_doe'] = 1000
        session.save()

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['user_name'], 'John Doe')
        self.assertEqual(response.context['user_not_login'], 'hidden')
        self.assertEqual(response.context['user_login'], 'show')

        self.assertEqual(response.context['cartItems'], 0)  
    def test_product_detail_view_no_session(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['user_not_login'], 'show')
        self.assertEqual(response.context['user_login'], 'hidden')

        self.assertEqual(response.context['cartItems'], 0)  

