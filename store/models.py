from django.db import models
from django.contrib.auth.models import User
import random
import string

def generate_tracking_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('fruits', 'Fruits'),
        ('vegetables', 'Vegetables'),
        ('dairy', 'Dairy'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
     
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField(blank=True)  # New field
    phone = models.CharField(max_length=15, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=15, unique=True, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = generate_tracking_number()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"


# Recommendation Model (AI-driven)
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_products = models.ManyToManyField(Product)

    def __str__(self):
        return f"Recommendations for {self.user.username}"



class ProductVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    visit_count = models.PositiveIntegerField(default=0)
    last_visited = models.DateTimeField(auto_now=True)  # Tracks the last visit time

    def __str__(self):
        return f"{self.user.username} visited {self.product.name} {self.visit_count} times"
