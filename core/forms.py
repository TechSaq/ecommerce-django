from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ('S', 'Stripe'),
        ('P', 'Paypal')
    )
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(Select Country)').formfield(
        required=False,
        widget=CountrySelectWidget(
            attrs={'class': 'custom-select d-block w-100',
                   'required': False
                   }
        ))
    shipping_zipcode = forms.CharField(required=False)

    billing_same_as_shipping = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(Select Country)').formfield(
        required=False,
        widget=CountrySelectWidget(
            attrs={'class': 'custom-select d-block w-100',
                   'required': False
                   }
        ))
    billing_zipcode = forms.CharField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_options = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(max_length=10, required=False,
                           widget=forms.TextInput(attrs={
                               'class': "form-control",
                               'placeholder': "Promo code",
                               'aria-label': "Recipient's username",
                               'aria-describedby': "basic-addon2"
                           }))
