from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
from .models import Order, Product, OrderItem, Recommendation, ProductVisit
from django.contrib.auth.models import User
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def generate_recommendations():
    """
    Generates product recommendations for each user based on past purchases and visits.
    """
    # Fetch all order items
    orders = OrderItem.objects.all().select_related("order", "product")

    # Create a DataFrame from order data
    data = []
    for item in orders:
        data.append([item.order.user.id, item.product.id, item.quantity])

    df = pd.DataFrame(data, columns=["user_id", "product_id", "quantity"])

    if df.empty:
        print("No order data available for recommendations.")
        return

    # Create a user-product matrix (rows: users, columns: products)
    user_product_matrix = df.pivot_table(index="user_id", columns="product_id", values="quantity", fill_value=0)

    # Compute cosine similarity between users
    user_sim_matrix = cosine_similarity(user_product_matrix)

    # Convert similarity matrix to a DataFrame
    user_sim_df = pd.DataFrame(user_sim_matrix, index=user_product_matrix.index, columns=user_product_matrix.index)

    # Generate recommendations for each user
    for user_id in user_product_matrix.index:
        similar_users = user_sim_df[user_id].sort_values(ascending=False).index[1:6]  # Top 5 similar users
        recommended_products = set()

        for similar_user in similar_users:
            # Get products that the similar user has purchased but the current user hasn't
            purchased_by_similar_user = set(df[df["user_id"] == similar_user]["product_id"])
            purchased_by_current_user = set(df[df["user_id"] == user_id]["product_id"])

            new_recommendations = purchased_by_similar_user - purchased_by_current_user
            recommended_products.update(new_recommendations)

        # Fetch the products the user has visited more than a threshold (e.g., 3 times)
        time_threshold = timezone.now() - timedelta(days=7)  # e.g., within the past 7 days
        visited_products = ProductVisit.objects.filter(
            user_id=user_id,
            visit_count__gte=3,  # Threshold for visits (3 visits)
            last_visited__gte=time_threshold
        ).values_list('product_id', flat=True)

        recommended_products.update(visited_products)

        # Save recommendations to the database
        user = User.objects.get(id=user_id)
        Recommendation.objects.filter(user=user).delete()  # Clear old recommendations
        rec_obj = Recommendation.objects.create(user=user)
        rec_obj.recommended_products.set(Product.objects.filter(id__in=recommended_products))

    print("AI recommendations updated successfully!")
