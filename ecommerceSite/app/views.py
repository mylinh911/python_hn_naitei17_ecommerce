from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomerForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.utils.translation import get_language, activate, gettext
from django.views import generic
from django.contrib.auth.models import User
# from ecommerceSite.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
import smtplib
from django.contrib.sessions.backends.db import SessionStore

# for API 
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CustomerSerializer, CustomerLoginSerializer, ProductSerializer, OrderDetailSerializer, OrderSerializer, AcceptOrderSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.sessions.models import Session

class CustomerAPIView(APIView):
    def get_required_fields(self):
        serializer = CustomerSerializer()
        required_fields = [field.field_name for field in serializer.fields.values() if field.required]
        return required_fields

    def post(self, request, *args, **kwargs):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        required_fields = self.get_required_fields()
        return Response({'required_fields': required_fields})

class CustomerLoginView(APIView):
    def get_required_fields(self):
        serializer = CustomerLoginSerializer()
        required_fields = [field.field_name for field in serializer.fields.values() if field.required]
        return required_fields

    def get(self, request, *args, **kwargs):
        required_fields = self.get_required_fields()
        return Response({'required_fields': required_fields})

    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_name = serializer.validated_data['user_name']
        password = serializer.validated_data['password']
        
        user = authenticate(request, user_name=user_name, password=password)
        
        if user is not None:
            login(request, user)
            session = SessionStore()
            session.create()
            session['customer_id'] = user.customer.userID
            session.save()
            return Response({'message': 'Đăng nhập thành công.', 'session_id': session.session_key})

        try:
            customer = Customer.objects.get(user_name=user_name)
            if customer.check_password(password):
                request.session['customer_id'] = customer.userID
                return Response({'message': 'Đăng nhập thành công.', 'session_id': request.session.session_key})
            else:
                return Response({'message': 'Mật khẩu không hợp lệ.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Customer.DoesNotExist:
            return Response({'message': 'Khách hàng không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

class ProductListView(APIView):
    def get(self, request):
        category_id = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        featured_only = request.GET.get('featured_only')

        products = Product.objects.all()

        if category_id:
            products = products.filter(category__id=category_id)


        if featured_only:
            products = products.filter(featured=True)

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)

class OrderPlacementAPIView(APIView):
    def get(self, request):
        serializer = OrderSerializer()
        required_fields = serializer.get_required_fields()
        return Response(required_fields, status=status.HTTP_200_OK)
        
    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()

            order.status = 'pending'  
            order.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class AcceptOrderView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(orderID=order_id)
            serializer = AcceptOrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, order_id):
        try:
            order = Order.objects.get(orderID=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if order.status != 'pending':
            return Response({'message': 'Order status cannot be changed'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'shipped'
        order.save()
        
        return Response({'message': 'Order status updated to shipped'}, status=status.HTTP_200_OK)
        
def check_user_id_in_session(request):
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    
    for value in session_values:
        if value in customer_ids:
            return True
    
    return False

def register(request):
    user_not_login = "hidden"
    user_login = "hidden"
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomerForm()
    return render(request, 'app/register.html', {'form': form, 'user_not_login':user_not_login, 'user_login':user_login})

def home(request, language = None):
    Order.objects.filter(status='demo').delete()
    cur_language = language or request.LANGUAGE_CODE
    activate(cur_language)
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    products = Product.objects.filter(featured=True)
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            user_not_login = "hidden"
            user_login = "show"
            order, created = Order.objects.get_or_create(customer = customer, status ='cart')
            cartItems = order.get_cart_items
            context = { 'cartItems': cartItems,'products': products,'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
            return render(request,'app/home.html',context)

    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
        context = { 'products': products,'user_name':request.user.last_name, 'user_not_login':user_not_login, 'user_login':user_login}
        return render(request,'app/home.html',context)
    
    user_not_login = "show"
    user_login = "hidden"
    context = {'products': products,'user_not_login':user_not_login, 'user_login':user_login}
    return render(request,'app/home.html',context)

def loginPage(request):
    Order.objects.filter(status='demo').delete()
    user_not_login = "hidden"
    user_login = "hidden"
    
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        try:
            customer = Customer.objects.get(user_name=username)
            if customer.check_password(password):
                request.session['customer_id'] = customer.userID
                
                return redirect('home')  
            else:
                error_message = 'Invalid password'
        except Customer.DoesNotExist:
            error_message = 'Customer does not exist'
        return render(request, 'app/login.html', {'error_message': error_message, 'user_not_login':user_not_login, 'user_login':user_login})
    else:
        return render(request, 'app/login.html', { 'user_not_login':user_not_login, 'user_login':user_login})

def logoutPage(request):
    Order.objects.filter(status='demo').delete()
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')

    if 'customer_id' in request.session:
        del request.session['customer_id']
    return redirect('login')

def productList(request):
    Order.objects.filter(status='demo').delete()
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    products = Product.objects.all()
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            user_not_login = "hidden"
            user_login = "show"
            order, created = Order.objects.get_or_create(customer = customer, status ='cart')
            cartItems = order.get_cart_items
            context = { 'cartItems': cartItems,'products': products,'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
            return render(request,'app/product.html',context)
    
    user_not_login = "show"
    user_login = "hidden"
    context = {'products': products,'user_not_login':user_not_login, 'user_login':user_login}
    return render(request,'app/product.html',context)

# def product_detail_view(request, primary_key):
#     product = get_object_or_404(Product, pk=primary_key)
#     return render(request, 'app/product_detail.html', context={'product': product})

class ProductDetailView(generic.DetailView):
    Order.objects.filter(status='demo').delete()

    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request  # Access the request object

        customer_ids = Customer.objects.values_list('userID', flat=True)
        session_values = request.session.values()

        for value in session_values:
            if value in customer_ids:
                customer = Customer.objects.get(userID=value)
                user_not_login = "hidden"
                user_login = "show"
                context['user_name'] = customer.full_name
                context['user_not_login'] = user_not_login
                context['user_login'] = user_login
                order, created = Order.objects.get_or_create(customer = customer, status ='cart')
                cartItems = order.get_cart_items
                context ['cartItems']= cartItems
                return context

        user_not_login = "show"
        user_login = "hidden"
        context ['cartItems']=0
        context['user_not_login'] = user_not_login
        context['user_login'] = user_login
        return context

def cart(request):
    Order.objects.filter(status='demo').delete()
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            order, created = Order.objects.get_or_create(customer=customer, status='cart')
            items = order.orderdetail_set.all()
            user_not_login = "hidden"
            user_login = "show"
            cartItems = order.get_cart_items
            context = {
                'cartItems': cartItems,
                'items': items,
                'order': order,
                'user_name': customer.full_name,
                'user_not_login': user_not_login,
                'user_login': user_login
            }
            return render(request, 'app/cart.html', context)

    user_not_login = "show"
    user_login = "hidden"
    items = []
    order = []
    cartItems = []
    context = {
        'items': items,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login
    }
    return render(request, 'app/cart.html', context)

def updateItem(request):
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            break
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    quantity = int(data.get('quantity', 0))
    product = Product.objects.get(productID=productId)
    order, created = Order.objects.get_or_create(customer=customer, status ='cart')
    orderItem, created = OrderDetail.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity += quantity
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()
    if action == 'delete':
        orderItem.delete()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse({'status': 'success'})

def checkoutDemo(request):
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            break
    data = json.loads(request.body)
    orderQuantityList = data['orderQuantityList']
    orderProductList = data['orderProductList']

    order = Order.objects.create(customer=customer, status='demo')

    for i in range(len(orderQuantityList)):
        product = Product.objects.get(productID=orderProductList[i])
        quantity = orderQuantityList[i]
        OrderDetail.objects.create(order=order, product=product, quantity=quantity)

    return JsonResponse({'status': 'success'})

def checkout(request):
    user_not_login = "hidden"
    user_login = "show"
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            if request.method == 'POST':
                province = request.POST.get('province')
                district = request.POST.get('district')
                commune = request.POST.get('commune')
                house_number = request.POST.get('house_number')

                information = house_number + ', ' + commune + ', ' + district + ', ' + province

                order = Order.objects.filter(customer=customer, status='demo').order_by('-order_date').first()
                cart = Order.objects.get(customer=customer, status='cart')
                cart_items = cart.orderdetail_set.all()
                pending_order = order.orderdetail_set.all()
                for cart_item in cart_items:
                    if pending_order.filter(product=cart_item.product).exists():
                        cart_item.delete()
                order.shipping_address = information
                print(information)
                order.status ='pending'
                order.save()

                staff_users = User.objects.filter(is_staff=True)
                staff_emails = [user.email for user in staff_users]
                email='linhttm193303@gmail.com'
                password = 'xxxxxx'
                email_sents = [customer.email]
                email_sents.extend(staff_emails)

                session = smtplib.SMTP('smtp.gmail.com', 587)
                session.starttls()
                session.login(email, password)

                subject = "ecommerce shop"

                customer_mail_content = f"Subject: {subject}\n\nBạn đã đặt hàng thành công".encode('utf-8')
                staff_mail_content = f"Subject: {subject}\n\nCó đơn đặt hàng mới".encode('utf-8')

                for recipient_email in email_sents:
                    if recipient_email == customer.email:
                        mail_content = customer_mail_content
                    else:
                        mail_content = staff_mail_content

                    session.sendmail(email, recipient_email, mail_content)

                session.quit()
                print('mail sent')
                return redirect('home')
            order = Order.objects.filter(customer=customer, status='demo').order_by('-order_date').first()

            items = order.orderdetail_set.all()
            user_not_login = "hidden"
            user_login = "show"
            cartItems = order.get_cart_items
            context = { 'cartItems': cartItems,'items':items, 'order': order, 'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
            return render(request,'app/checkout.html',context)

    
    items = []
    order = {'get_cart_items':0, 'get_cart_total':0}
    cartItems = order['get_cart_items']
    context = {'items': items, 'cartItems':cartItems , 'user_not_login':user_not_login, 'user_login':user_login  }
    return render(request,'app/checkout.html',context)

def orderlist(request, language = None):
    Order.objects.filter(status='demo').delete()
    cur_language = language or request.LANGUAGE_CODE
    activate(cur_language)
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            user_not_login = "hidden"
            user_login = "show"
            orders = Order.objects.filter(customer=customer).exclude(status__in=['demo', 'cart'])
            order, created = Order.objects.get_or_create(customer = customer, status ='cart')
            if order is None:
                cartItems = '0'
            else:
                cartItems = order.get_cart_items
            is_staff = "hidden"
            context = { 'is_staff': is_staff,'cartItems': cartItems,'orders': orders,'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
            return render(request,'app/orderlist.html',context)

    if request.user.is_authenticated:
        if request.method == 'POST':
            order_id = request.POST.get('order_id')
            order = Order.objects.get(pk=order_id)
            order.status = 'shipped'
            order.save()
        user_not_login = "hidden"
        user_login = "show"
        orders = Order.objects.exclude(status__in=['demo', 'cart'])
        cartItems = '0'
        is_staff = "show"
        context = { 'is_staff': is_staff, 'cartItems': cartItems,'orders': orders,'user_name':request.user.last_name, 'user_not_login':user_not_login, 'user_login':user_login}
        return render(request,'app/orderlist.html',context)


    
    user_not_login = "show"
    user_login = "hidden"
    context = {'user_not_login':user_not_login, 'user_login':user_login}
    return render(request,'app/orderlist.html',context)
    
class OrderDetailView(generic.DetailView):
    Order.objects.filter(status='demo').delete()

    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request  # Access the request object

        customer_ids = Customer.objects.values_list('userID', flat=True)
        session_values = request.session.values()

        for value in session_values:
            if value in customer_ids:
                customer = Customer.objects.get(userID=value)
                user_not_login = "hidden"
                user_login = "show"
                context['user_name'] = customer.full_name
                context['user_not_login'] = user_not_login
                context['user_login'] = user_login
                return context

        user_not_login = "show"
        user_login = "hidden"
        context['user_not_login'] = user_not_login
        context['user_login'] = user_login
        return context

    def post(self, request, *args, **kwargs):
        order = self.get_object()

        if 'cancel_order' in request.POST:
            reason = request.POST.get('reason')
            order.status = 'canceled'
            order.cancel_order(reason)

            order.save(update_fields=['status'])

        Order.objects.filter(status='demo').delete()
        customer_ids = Customer.objects.values_list('userID', flat=True)
        session_values = request.session.values()
        for value in session_values:
            if value in customer_ids:
                customer = Customer.objects.get(userID=value)
                user_not_login = "hidden"
                user_login = "show"
                orders = Order.objects.filter(customer=customer).exclude(status__in=['demo', 'cart'])
                context = { 'orders': orders,'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
                return render(request,'app/orderlist.html',context)
