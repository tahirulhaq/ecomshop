from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('signup/', views.signUp, name='signup'),
    path('customerRegister/', views.customerRegister, name='customerRegister'),
    path('cart/', views.cartView, name='cart'),
    path('checkout/', views.checkOut, name='checkout'),
    path('orders', views.orderView, name='orders'),
    path('product/<id>/<slug>', views.product_details, name='product'),
    path('addToCart/<id>/<slug>', views.addToCart, name='addToCart'),
    path('deleteOrder/<id>', views.deleteOrder, name='deleteOrder'),
    path('removeItem/<id>/<slug>', views.removeItem, name='removeItem'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         views.activate, name='activate'),
    path('checkoutPage/', views.checkoutView, name='checkoutPage'),
    path('checkoutData/', views.checkoutData, name='checkoutData'),


]
