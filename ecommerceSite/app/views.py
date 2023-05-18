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
            context = {'products': products,'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
            return render(request,'app/home.html',context)
    
    user_not_login = "show"
    user_login = "hidden"
    context = {'products': products,'user_not_login':user_not_login, 'user_login':user_login}
    return render(request,'app/home.html',context)

def loginPage(request):
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
    if 'customer_id' in request.session:
        del request.session['customer_id']
    return redirect('login')

def productList(request):
    customer_ids = Customer.objects.values_list('userID', flat=True)
    session_values = request.session.values()
    products = Product.objects.all()
    for value in session_values:
        if value in customer_ids:
            customer = Customer.objects.get(userID=value)
            user_not_login = "hidden"
            user_login = "show"
            context = {'products': products,'user_name':customer.full_name, 'user_not_login':user_not_login, 'user_login':user_login}
            return render(request,'app/product.html',context)
    
    user_not_login = "show"
    user_login = "hidden"
    context = {'products': products,'user_not_login':user_not_login, 'user_login':user_login}
    return render(request,'app/product.html',context)

# def product_detail_view(request, primary_key):
#     product = get_object_or_404(Product, pk=primary_key)
#     return render(request, 'app/product_detail.html', context={'product': product})

class ProductDetailView(generic.DetailView):
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
                return context

        user_not_login = "show"
        user_login = "hidden"
        context['user_not_login'] = user_not_login
        context['user_login'] = user_login
        return context

    

