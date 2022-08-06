from django.urls import path

from . import views

urlpatterns = [
    path('payment/', views.viewPayment, name='payment'),
    path('config/', views.stripe_config, name='config'),
    path('create-checkout-session/', views.create_checkout_session,
         name='create-checkout-session'),
    path('success/', views.successView, name='success'),
    path('cancelled/', views.cancelledView, name='cancelled'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]
