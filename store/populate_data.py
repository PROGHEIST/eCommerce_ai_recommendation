from django.contrib.auth.models import User
from .models import Product, Order, OrderItem

# Create users
users = [
    {"username": "user1", "email": "user1@example.com", "password": "password123"},
    {"username": "user2", "email": "user2@example.com", "password": "password123"},
    {"username": "user3", "email": "user3@example.com", "password": "password123"},
    {"username": "user4", "email": "user4@example.com", "password": "password123"},
]

for user_data in users:
    user = User.objects.create_user(**user_data)
    user.save()

# Create products
products = [
    {"name": "Apple", "category": "fruits", "price": 10.00, "stock": 100, "description": "Fresh apples"},
    {"name": "Banana", "category": "fruits", "price": 5.00, "stock": 100, "description": "Fresh bananas"},
    {"name": "Carrot", "category": "vegetables", "price": 8.00, "stock": 100, "description": "Fresh carrots"},
    {"name": "Milk", "category": "dairy", "price": 20.00, "stock": 100, "description": "Fresh milk"},
    {"name": "Orange Juice", "category": "beverages", "price": 15.00, "stock": 100, "description": "Fresh orange juice"},
    {"name": "Chips", "category": "snacks", "price": 25.00, "stock": 100, "description": "Crispy chips"},
    {"name": "Yogurt", "category": "dairy", "price": 12.00, "stock": 100, "description": "Fresh yogurt"},
    {"name": "Soda", "category": "beverages", "price": 10.00, "stock": 100, "description": "Refreshing soda"},
]

for product_data in products:
    product = Product.objects.create(**product_data)
    product.save()

# Create orders
orders = [
    {"user": User.objects.get(username="user1"), "total_price": 30.00, "address": "123 Street", "phone": "1234567890"},
    {"user": User.objects.get(username="user2"), "total_price": 20.00, "address": "456 Street", "phone": "0987654321"},
]

for order_data in orders:
    order = Order.objects.create(**order_data)
    order.save()

# Create order items
order_items = [
    {"order": Order.objects.get(id=1), "product": Product.objects.get(name="Apple"), "quantity": 2, "price": 10.00},
    {"order": Order.objects.get(id=1), "product": Product.objects.get(name="Banana"), "quantity": 2, "price": 5.00},
    {"order": Order.objects.get(id=2), "product": Product.objects.get(name="Carrot"), "quantity": 2, "price": 8.00},
    {"order": Order.objects.get(id=2), "product": Product.objects.get(name="Milk"), "quantity": 1, "price": 20.00},
]

for order_item_data in order_items:
    order_item = OrderItem.objects.create(**order_item_data)
    order_item.save()
