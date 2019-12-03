from django.contrib import admin
from .models import Item, Order, OrderItem, Address, Payment, Coupon, Category


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'billing_address',
                    'shipping_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = ['user',
                          'billing_address',
                          'shipping_address',
                          'payment',
                          'coupon'
                          ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received'
                   ]
    search_fields = ['user__username',
                     'ref_code']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'street_address',
                    'apartment_address',
                    'country',
                    'zipcode',
                    'address_type',
                    'default']
    list_filter = ['default',
                   'zipcode',
                   'country'
                   ]
    search_fields = ['user',
                     'street_address',
                     'apartment_address',
                     'zipcode']


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title', 'image', 'price', 'category']
    list_filter = ['category']


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Category, CategoryAdmin)
