from django import forms
from .models import ShippingAddress

class ShippingForm(forms.ModelForm):
    shipping_full_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder':'Полное имя'}), required=True)
    shipping_email = forms.CharField(label="", widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder':'Адрес почты'}), required=True)
    shipping_address = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Улица, дом, квартира'}), required=True)
    shipping_city = forms.CharField(label="", widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder':'Город'}), required=True)


    class Meta:
        model = ShippingAddress
        fields = ['shipping_full_name', 'shipping_email', 'shipping_address']
        exclude = ['user',]

class PaymentForm(forms.Form):
	pass
