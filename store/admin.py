from django.contrib import admin
from .models import Product, Order, Recommendation, OrderItem, ProductVisit, ContactMessage, ProductReview

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'tracking_number')
    list_filter = ('status',)
    search_fields = ('tracking_number',)
    
admin.site.register(ProductVisit)
admin.site.register(OrderItem)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'market_price', 'selling_price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'category')
    ordering = ('category', 'name')
admin.site.register(Recommendation)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')

admin.site.register(ProductReview)