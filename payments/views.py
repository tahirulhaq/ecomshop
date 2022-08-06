from math import prod
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings  # new
from django.http.response import JsonResponse  # new
from django.views.decorators.csrf import csrf_exempt
from store.models import Product
import stripe  # new

# Create your views here.


def viewPayment(request):
    formData = request.session['formData']
    email = formData['email']
    print(formData)
    cart = request.session['cart']
    print(cart)
    return render(request, 'payments/payment.html', {'email': email})


def successView(request):
    return redirect('checkout')


def cancelledView(request):
    return render(request, 'payments/cancelled.html', {})


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    # create product list
    my_list = []
    my_dict = {"name": [], "quantity": 1, "currency": "pkr", 'amount': ''}
    cart = request.session['cart']
    ids = list(request.session.get('cart').keys())
    products = Product.get_products_by_id(ids)
    print(products)
    for product in products:
        my_dict["name"] = product.name
        my_dict["quantity"] = cart[str(product.id)]
        my_dict["amount"] = str(product.price*100)
        my_list.append(my_dict)

        my_dict = {"name": [], "quantity": 1, "currency": "pkr", 'amount': ''}

    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url +
                'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=my_list
                # [
                #     {
                #         'name': 'Women Saree Large Size',
                #         'quantity': 1,
                #         'currency': 'pkr',
                #         'amount': '1000000',
                #     },
                #     {
                #         'name': 'Saree Modern',
                #         'quantity': 1,
                #         'currency': 'pkr',
                #         'amount': '2500000',
                #     }
                # ]

            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)
