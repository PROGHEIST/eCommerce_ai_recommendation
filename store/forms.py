# forms.py

from django import forms

class CheckoutForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea, required=True)
    phone = forms.CharField(max_length=15, required=True)
