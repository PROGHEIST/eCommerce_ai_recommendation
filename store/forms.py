from django import forms
from .models import ProductReview

class CheckoutForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea, required=True)
    phone = forms.CharField(max_length=15, required=True)



class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Rate (1 to 5)'
            }),
            'review': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full p-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Write your review here...'
            }),
        }
