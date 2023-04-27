from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('products/', views.productList, name='products'),
    path('product/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),

]
