from django.contrib import admin
from .models import Product, Order, Recommendation, OrderItem, ProductVisit

admin.site.register(Order)
admin.site.register(ProductVisit)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(Recommendation)