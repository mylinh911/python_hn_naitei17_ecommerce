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
            order, created = Order.objects.get_or_create(customer = customer, status ='cart')
            items = order.orderdetail_set.all()
            user_not_login = "hidden"
            user_login = "show"
            cartItems = order.get_cart_items
            context = { 'cartItems': cartItems,'items':items, 'order': order, 'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
            return render(request,'app/cart.html',context)
    
    user_not_login = "show"
    user_login = "hidden"
    items = []
    order = {'get_cart_items':0, 'get_cart_total':0}
    cartItems = order.get_cart_items
    context = {'items':items, 'cartItems': cartItems,'order': order,'user_not_login':user_not_login, 'user_login':user_login}
    return render(request,'app/cart.html',context)

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

    

