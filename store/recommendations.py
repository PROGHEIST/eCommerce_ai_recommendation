from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
from .models import OrderItem, Product
from django.contrib.auth.models import User
from sklearn.neighbors import NearestNeighbors
import pandas as pd

def generate_recommendations(user):
    """
    Generates product recommendations for a user based on past purchases.
    """
    # Fetch all order items
    orders = OrderItem.objects.all().select_related("order", "product")

    # Create a DataFrame from order data
    data = []
    for item in orders:
        data.append([item.order.user.id, item.product.id, item.quantity])

    df = pd.DataFrame(data, columns=["user_id", "product_id", "quantity"])

    if df.empty:
        return []

    # Create a user-product matrix (rows: users, columns: products)
    user_product_matrix = df.pivot_table(index="user_id", columns="product_id", values="quantity", fill_value=0)

    # Train KNN model
    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(user_product_matrix)

    try:
        # Find similar users
        user_index = user_product_matrix.index.get_loc(user.id)
        n_neighbors = min(6, len(user_product_matrix))
        distances, indices = knn.kneighbors(user_product_matrix.iloc[user_index, :].values.reshape(1, -1), n_neighbors=n_neighbors)

        # Get recommended products
        similar_users = indices.flatten()[1:]
        recommended_products = set()

        for similar_user in similar_users:
            similar_user_id = user_product_matrix.index[similar_user]
            purchased_by_similar_user = set(df[df["user_id"] == similar_user_id]["product_id"])
            purchased_by_current_user = set(df[df["user_id"] == user.id]["product_id"])

            new_recommendations = purchased_by_similar_user - purchased_by_current_user
            recommended_products.update(new_recommendations)

        return Product.objects.filter(id__in=recommended_products)
    except KeyError as e:
        print(f"KeyError: {e}")
        return []
