from gc import collect
from itertools import product
from math import prod
from multiprocessing import context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import clear_url_caches
from django.contrib.sites.shortcuts import get_current_site
from store.forms import CustomerForm, UserRegisterForm
from .models import Category, Product, Customer, Order
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
# Create your views here.


def cart_quantity(product, cart):
    keys = cart.keys()
    for id in keys:
        if int(id) == product.id:
            return cart.get(id)
    return 0


def home(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    categories = Category.objects.all()
    products = Product.objects.all()

    context = {'categories': categories, 'products': products}
    return render(request, 'store/home.html', context)


def addToCart(request, id, slug):

    # product id from product_detail.html
    product = request.POST.get('product')
    remove = request.POST.get('remove')     # boolean
    cart = request.session.get('cart')
    if cart:
        quantity = cart.get(product)
        if quantity:
            if remove:
                if quantity <= 1:
                    cart.pop(product)
                else:
                    cart[product] = quantity-1
            else:
                cart[product] = quantity+1
                print('item added')

        else:
            cart[product] = 1
    else:
        cart = {}
        cart[product] = 1

    request.session['cart'] = cart
    # print(request.session['cart'])

    # go back to product page
    productA = Product.objects.get(id=id)
    categoryA = Category.objects.get(slug=slug)
    context = {'product': productA, 'category': categoryA}

    return render(request, 'store/product_detail.html', context)

# remove item


def removeItem(request, id, slug):
    cart = request.session.get('cart')
    if cart:
        quantity = cart.get(id)
        if quantity:
            cart.pop(id)
    request.session['cart'] = cart
    print(request.session['cart'])
    # go back to product page
    productA = Product.objects.get(id=id)
    categoryA = Category.objects.get(slug=slug)
    context = {'product': productA, 'category': categoryA}
    return render(request, 'store/product_detail.html', context)

# delete order


def deleteOrder(request, id):
    customer = request.session.get('customer-id')
    Order.get_specific_order(customer, id).delete()

    orders = Order.get_orders_by_customer(customer)
    return render(request, 'store/orders.html', {'orders': orders})


def loginUser(request):
    page = 'login'

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            HttpResponse('User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            HttpResponse('Username OR password does not exist')
    context = {'page': page}
    return render(request, 'store/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def customerRegister(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            customer = Customer.get_customer_by_email(email)
            request.session['customer'] = customer.id
        return redirect('cart')

    context = {'form': form}
    return render(request, 'store/customer_register.html', context)


def signUp(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('store/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            HttpResponse('An error occured during registration')
    return render(request, 'store/login.html', {'form': form})


def cartView(request):
    ids = list(request.session.get('cart').keys())
    products = Product.get_products_by_id(ids)
    print(products)
    for product in products:
        print(product.price)
    return render(request, 'store/cart.html', {'products': products})


def checkoutView(request):
    cart = request.session['cart']
    if cart:
        return render(request, 'store/checkout.html', {})
    else:
        return render(request, 'store/cart.html', {'products': {}, 'message': 'Cart is empty cannot checkout'})


def checkoutData(request):
    # post variables
    first_name = request.POST.get('fname')
    last_name = request.POST.get('lname')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    address = request.POST.get('address')

    # stored variables in session
    formData = request.session.get('formData')
    formData = {}
    formData['first_name'] = first_name
    formData['last_name'] = last_name
    formData['phone'] = phone
    formData['email'] = email
    formData['address'] = address
    # print(formData)
    # print(formData['email'])
    request.session['formData'] = formData
    return redirect('payment')


def checkOut(request):
    # session formData
    formData = request.session['formData']
    print(formData)
    first_name = formData['first_name']
    last_name = formData['last_name']
    phone = formData['phone']
    email = formData['email']
    address = formData['address']

    ## sessions and products
    cart = request.session['cart']
    ids = list(request.session.get('cart').keys())
    products = Product.get_products_by_id(ids)

    # fetch customer object
    customer = Customer.get_customer_by_email(email)
    # print(customer)
    if not customer:
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone
        )
        print("We created a new customer")
    else:
        print('Customer exists')

    # get customer newly created
    customer = Customer.get_customer_by_email(email)

    # set session of customer
    request.session['customer-id'] = customer.id

    if customer:
        for product in products:
            order = Order.objects.create(
                product=product,
                customer=customer,
                quantity=cart_quantity(product, cart),
                price=product.price,
                address=address,
                phone=phone
            )
        message = 'Order placed Successfully.'
        request.session['cart'] = {}
        customer = request.session.get('customer-id')
        orders = Order.get_orders_by_customer(customer)
        return render(request, 'store/orders.html', {'orders': orders, 'message': message})
    message = 'Order not placed. Order Already Placed.'
    return render(request, 'store/cart.html', {'products': products, 'message': message})


def orderView(request):
    customer = request.session.get('customer-id')
    orders = Order.get_orders_by_customer(customer)
    # print(orders)
    return render(request, 'store/orders.html', {'orders': orders})


def product_details(request, id, slug):
    product = Product.objects.get(id=id)
    category = Category.objects.get(slug=slug)
    context = {'product': product, 'category': category}
    return render(request, 'store/product_detail.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.<a href="http://127.0.0.1:8000/">Go to Home</a>')
    else:
        return HttpResponse('Activation link is invalid!')
