from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone

from .models import Item, OrderItem, Order, Address, Payment, Coupon, Category
from .forms import CheckoutForm, CouponForm

import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class HomeView(ListView):
    model = Category
    template_name = "home.html"


class ProductView(ListView):
 
    def get(self, *args, **kwargs):
        
        category = self.kwargs['slug']
        c = ''
        if category == 'mens-fashion':
            c = 'MP'
        if category == 'womens-fashion':
            c = 'WP'
        if category == 'kids-fashion':
            c = 'KP'
        if category == 'stationery':
            c = 'SP'
        if category == 'home-kitchen':
            c = 'HKP'
        if category == 'sports-fitness':
            c = 'SFP'
        if category == 'electronics':
            c = 'EP'

        qs = Item.objects.filter(category=c)
        context = {
            'object_list': qs
        }
        return render(self.request, 'product.html', context)

     
class ItemDetailView(DetailView):
    model = Item
    template_name = "product-detail.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, "order_summary.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You don't have any active order!!")
            return redirect("/")


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponForm': CouponForm(),
                'order': order,
                "DISPLAY_COUPON_FORM": True
            }
            
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            
            if shipping_address_qs.exists():
                context.update({'default_shipping_adress': shipping_address_qs[0]})
                
            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            
            if billing_address_qs.exists():
                context.update({'default_billing_adress': billing_address_qs[0]})
            
        except ObjectDoesNotExist:
            messages.info(self.request, "Currently you don't have any ordrs")
            return redirect("/")
        
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                print("inside form valid")
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("using the default shipping address")
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'S',
                        default=True
                    )
                    print(address_qs)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default Shipping Address available")
                        return redirect("core:checkout")
                else:
                    print("user is entering the shipping address")
                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    print("-------------------------------------")
                    print(shipping_address1)
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zipcode = form.cleaned_data.get('shipping_zipcode')
                    
                    if is_valid_form([shipping_address1, shipping_country, shipping_zipcode]):
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address1,
                            apartment_address = shipping_address2,
                            country = shipping_country,
                            zipcode = shipping_zipcode,
                            address_type = 'S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                        
                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.warning(self.request, "Please fill the valid values!!")
                        return redirect("core:checkout")
                        
                use_default_billing = form.cleaned_data.get('use_default_billing')
                billing_same_as_shipping = form.cleaned_data.get('billing_same_as_shipping')
                if billing_same_as_shipping:
                    print("using same shipping address for billing")
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    print("using the default billing address")
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'B',
                        default=True
                    )
                    
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default Billing Address available")
                        return redirect("core:checkout")
                else:
                    print("user is entering the billing address")
                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zipcode = form.cleaned_data.get('billing_zipcode')
                    
                    if is_valid_form([billing_address1, billing_country, billing_zipcode]):
                        billing_address = Address(
                            user = self.request.user,
                            street_address = billing_address1,
                            apartment_address = billing_address2,
                            country = billing_country,
                            zipcode = billing_zipcode,
                            address_type = 'B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()
                        
                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.warning(self.request, "Please fill the valid values!!")
                        return redirect("core:checkout")
            else:
                print(form.cleaned_data)
                messages.warning(self.request, "Invalid form")
                return redirect("core:checkout")

            payment_options = form.cleaned_data.get('payment_options')
            if payment_options == 'S':
                print("in payment s")
                return redirect('core:payment', payment_option="stripe")
            elif payment_options == 'P':
                print("in payment p")
                return redirect('core:payment', payment_option="stripe")
            else:
                messages.warning(self.request, "Invalid payment option selected!")
                return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You don't have any active order!!")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                "DISPLAY_COUPON_FORM": False
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(self.request, "Add billing address first")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_cart_total())

        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                    amount=amount*100,
                    currency="inr",
                    source=token,
                )

            # create payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_cart_total()
            payment.save()
            
            order_item = order.items.all()
            order_item.update(ordered=True)
            for item in order_item:
                item.save()
            
            # assign the payment to the order
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            
            messages.success(self.request, "Your order was successfully placed...")
            return redirect("/")
        except stripe.error.CardError as e:
            messages.warning(self.request, f"{ e.error.message }")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, 'Rate Limit Error')
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, 'Invalid parameters')
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, 'Not Authenticated')
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, 'Network error')
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request, 'Something went wrong. You were not charged. Try Again!!')
            return redirect("/")
        except Exception as e:
            # send an emaill to ourselves
            messages.warning(self.request, 'A serious occured. We are notified and working on it.')
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, 'This item is added to your cart')
            order.items.add(order_item)
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        messages.info(request, "This item is added to your cart")
        order.items.add(order_item)
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.quantity = 1
            order_item.save()
            order.items.remove(order_item)
            messages.info(request, "This item is removed from your cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item is not in your cart")
            return redirect("core:product-detail", slug=slug)
    else:
        messages.info(request, "You don't have any order yet.")
        return redirect("core:product-detail", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item is updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item is not in your cart")
            return redirect("core:product-detail", slug=slug)
    else:
        messages.info(request, "You don't have any order yet.")
        return redirect("core:product-detail", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, "This coupon code is Invalid!!")
        return redirect("core:checkout")


class AddCoupon(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "This coupon code is Valid!!")
                return redirect("core:checkout")
                
            except ObjectDoesNotExist:
                messages.info(self.request, "Currently you don't have any orders")
                return redirect("/")