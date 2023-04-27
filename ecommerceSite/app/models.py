from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import  check_password, make_password
from django.urls import reverse

# Create your models here.
class Customer(models.Model):
    userID = models.AutoField(primary_key=True, editable=False)
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=10)
    

    def check_password(self, password):
        if (self.password==password):
            return True
        else:
            return False

class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null = True, blank = True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    productID = models.AutoField(primary_key=True)
    category = models.ManyToManyField(Category, related_name='product')
    name = models.CharField(max_length=200,null=True)
    description = models.CharField(max_length=2000,null=True)
    price = models.FloatField()
    image = models.ImageField(null=True,blank=True)
    featured = models.BooleanField(default=False, null=True, blank=False)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', args=[str(self.productID)])

    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('cart', 'Giỏ hàng'),
        ('demo', 'Xem trước'),
        ('pending', 'Đang chờ xử lý'),
        ('shipped', 'Đã gửi hàng'),
        ('delivered', 'Đã giao hàng'),
        ('canceled', 'Đã hủy'),
    ]

    orderID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='cart') 
    shipping_address = models.CharField(max_length=100, default='')
    canceled_reason = models.CharField(max_length=100, blank=True)

    def cancel_order(self, reason):
        if self.status == 'canceled':
            self.canceled_reason = reason
            self.save()
        else:
            raise ValueError("Cannot cancel an order that is not in 'canceled' status")

    def __str__(self):
        return str(self.pk)

    def ship_order(self):
        self.status = 'shipped'
        self.save()

    @property
    def get_cart_items(self):
        orderitems = self.orderdetail_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    @property
    def get_cart_total(self):
        orderitems = self.orderdetail_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    def get_absolute_url(self):
        return reverse('order-detail', args=[str(self.orderID)])


class OrderDetail(models.Model):
    productID = models.ForeignKey(Product,on_delete=models.SET_NULL, blank=True, null=True)
    orderID = models.ForeignKey(Order,on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        return str(self.pk)




