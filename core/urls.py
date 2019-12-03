from django.urls import path
from .views import (HomeView,
                    CheckoutView,
                    ItemDetailView,
                    add_to_cart,
                    remove_from_cart,
                    OrderSummaryView,
                    remove_single_item_from_cart,
                    PaymentView,
                    AddCoupon,
                    ProductView
                    )
app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('products/<slug>', ProductView.as_view(), name='products'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product-detail/<slug>/', ItemDetailView.as_view(), name='product-detail'),
    path('add-to-cart/<slug>', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>', remove_from_cart, name="remove-from-cart"),
    path('order-summary', OrderSummaryView.as_view(), name="order-summary"),
    path('remove-single-item-from-cart/<slug>',
         remove_single_item_from_cart, name="remove-single-item-from-cart"),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('add-coupon/', AddCoupon.as_view(), name='add-coupon'),


]
