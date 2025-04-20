import django
import os
import random
from django.contrib.auth.models import User
from store.models import Product, Order

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocery_ai.grocery_ai.settings")
django.setup()

# Ensure you have users and products in your database before adding orders
users = list(User.objects.all())
products = list(Product.objects.all())

if not users:
    print("No users found! Create users before adding orders.")
else:
    for _ in range(10):  # Creating 10 random orders
        user = random.choice(users)
        product = random.choice(products)
        quantity = random.randint(1, 5)
        total_price = product.price * quantity

        Order.objects.create(user=user, product=product, quantity=quantity, total_price=total_price)

    print("Sample orders added successfully!")
