from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

LABEL_CHOICES = {
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
}

ADDRESS_CHOICES = {
    ('B', 'Billing'),
    ('S', 'Shipping')
}

CATEGORY_CHOICES = [
        ('NO', 'SELECT CATEGORY'),
        ('MP', 'Mens Products'),
        ('WP', 'Womens Products'),
        ('KP', 'Kids Products'),
        ('SP', 'Stationery Products'),
        ('HKP', 'Home Kitchen Products'),
        ('SFP', 'Sports Fitness Products'),
        ('EP', 'Electronics Products')
    ]


class Category(models.Model):
    title = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='SELECT CATEGORY')
    image = models.ImageField()
    slug = models.SlugField(unique=True, null=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:products", kwargs={"slug": self.slug})
    
    
    class Meta:
        verbose_name_plural = 'Categories'


class Item(models.Model):
    image = models.ImageField(null=True, blank=True)
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product-detail",
                       kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart",
                       kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart",
                       kwargs={"slug": self.slug})


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity*self.item.price

    def get_total_discount_item_price(self):
        return self.quantity*self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey("Address",
                                        related_name="billing_address",
                                        on_delete=models.SET_NULL,
                                        blank=True, null=True)
    shipping_address = models.ForeignKey("Address",
                                         related_name="shipping_address",
                                         on_delete=models.SET_NULL,
                                         blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL,
                                blank=True, null=True)
    coupon = models.ForeignKey("Coupon", on_delete=models.CASCADE,
                               blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    # refund_requested = models.BooleanField(default=False)
    # refund_granted = models.BooleanField(default=False)

    # '''
    # 1. item added to cart
    # 2. Billing Adderess
    # (Failed Chekcout)
    # 3. Payment
    # (preprocessing, processing, packaging etc)
    # 4. Being delivered
    # 5. Received
    # 6. Refunds
    # '''
    def __str__(self):
        return self.user.username

    def get_cart_total(self):
        total = 0.0
        for order_item in self.items.all():
            total += order_item.get_final_price()

        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zipcode = models.CharField(max_length=100, null=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=10)
    amount = models.FloatField()

    def __str__(self):
        return self.code
