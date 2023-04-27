from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('checkout/', views.checkout, name="checkout"),
    path('orderlist/', views.orderlist, name="orderlist"),
    path('checkout_demo/', views.checkoutDemo, name="checkout_demo"),
    path('products/', views.productList, name='products'),
    path('cart/', views.cart, name='cart'),
    path('update_item/', views.updateItem, name='update_item'),
    path('product/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('order/<int:pk>', views.OrderDetailView.as_view(), name='order-detail'),

]
