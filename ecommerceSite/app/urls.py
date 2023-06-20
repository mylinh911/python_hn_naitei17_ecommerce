from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

# API URLs
api_patterns = [
    path('v1/register/', views.CustomerAPIView.as_view(), name='register-api'),
]

# Web URLs
web_patterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('orderlist/', views.orderlist, name='orderlist'),
    path('checkout_demo/', views.checkoutDemo, name='checkout_demo'),
    path('products/', views.productList, name='products'),
    path('cart/', views.cart, name='cart'),
    path('update_item/', views.updateItem, name='update_item'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    path('', include(web_patterns)),
]
