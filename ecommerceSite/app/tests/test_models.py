from django.test import TestCase
from django.urls import reverse
from app.models import Customer, Category, Product, Order, OrderDetail

class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            user_name='testuser',
            password='testpassword',
            email='test@example.com',
            full_name='Test User',
            address='Test Address',
            phone='1234567890'
        )

    def test_check_password(self):
        self.assertTrue(self.customer.check_password('testpassword'))
        self.assertFalse(self.customer.check_password('wrongpassword'))

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

    def test_str(self):
        self.assertEqual(str(self.category), 'Test Category')

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.99,
        )
        self.product.category.add(self.category)

    def test_str(self):
        self.assertEqual(str(self.product), 'Test Product')

    def test_get_absolute_url(self):
        url = reverse('product-detail', args=[str(self.product.productID)])
        self.assertEqual(self.product.get_absolute_url(), url)

class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            user_name='testuser',
            password='testpassword',
            email='test@example.com',
            full_name='Test User',
            address='Test Address',
            phone='1234567890'
        )
        self.order = Order.objects.create(
            customer=self.customer,
            status='canceled',
            shipping_address='Test Address'
        )

    def test_cancel_order(self):
        self.order.cancel_order('Test Reason')
        self.assertEqual(self.order.status, 'canceled')
        self.assertEqual(self.order.canceled_reason, 'Test Reason')

    def test_cancel_order_invalid_status(self):
        self.order.status = 'shipped'
        self.order.save()
        with self.assertRaises(ValueError):
            self.order.cancel_order('Test Reason')

    def test_str(self):
        self.assertEqual(str(self.order), str(self.order.pk))

    def test_ship_order(self):
        self.order.ship_order()
        self.assertEqual(self.order.status, 'shipped')

    def test_get_cart_items(self):
        OrderDetail.objects.create(
            product=Product.objects.create(name='Test Product', price=10.99),
            order=self.order,
            quantity=2
        )
        self.assertEqual(self.order.get_cart_items, 2)

    def test_get_cart_total(self):
        OrderDetail.objects.create(
            product=Product.objects.create(name='Test Product', price=10.99),
            order=self.order,
            quantity=2
        )
        self.assertEqual(self.order.get_cart_total, 21.98)

    def test_get_absolute_url(self):
        url = reverse('order-detail', args=[str(self.order.orderID)])
        self.assertEqual(self.order.get_absolute_url(), url)

class OrderDetailModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            user_name='testuser',
            password='testpassword',
            email='test@example.com',
            full_name='Test User',
            address='Test Address',
            phone='1234567890'
        )
        self.order = Order.objects.create(
            customer=self.customer,
            status='cart',
            shipping_address='Test Address'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=10.99
        )
        self.order_detail = OrderDetail.objects.create(
            product=self.product,
            order=self.order,
            quantity=2
        )

    def test_str(self):
        self.assertEqual(str(self.order_detail), str(self.order_detail.pk))
