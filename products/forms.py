from django import forms
from .models import Order, DeliveryAddress

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['full_name', 'phone_number', 'province', 'district', 'location', 'street_address', 'landmark', 'postal_code', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter province/state'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter district'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city/municipality'}),
            'street_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter detailed street address'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter nearby landmark (optional)'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter postal code (optional)'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'full_name': 'Full Name',
            'phone_number': 'Phone Number',
            'province': 'Province/State',
            'district': 'District',
            'location': 'City/Municipality',
            'street_address': 'Street Address',
            'landmark': 'Landmark',
            'postal_code': 'Postal Code',
            'is_default': 'Set as default address',
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'phone_number']
