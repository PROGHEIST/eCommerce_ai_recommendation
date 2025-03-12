from django.contrib import admin
from .models import Product, Order, Recommendation, OrderItem, ProductVisit

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'tracking_number')
    list_filter = ('status',)
    search_fields = ('tracking_number',)
    
admin.site.register(ProductVisit)
admin.site.register(OrderItem)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'category')
    ordering = ('category', 'name')
admin.site.register(Recommendation)