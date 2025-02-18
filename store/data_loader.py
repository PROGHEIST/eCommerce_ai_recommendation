from store.models import Product


sample_products = [
    {"name": "Apple", "category": "fruits", "price": 1.50, "stock": 100, "description": "Fresh apples."},
    {"name": "Banana", "category": "fruits", "price": 0.50, "stock": 200, "description": "Organic bananas."},
    {"name": "Milk", "category": "dairy", "price": 2.00, "stock": 50, "description": "1L full-cream milk."},
    {"name": "Bread", "category": "snacks", "price": 1.80, "stock": 80, "description": "Whole wheat bread."},
    {"name": "Orange Juice", "category": "beverages", "price": 3.00, "stock": 60, "description": "100% pure orange juice."},
]

for product in sample_products:
    Product.objects.create(**product)

print("Sample products added successfully!")
