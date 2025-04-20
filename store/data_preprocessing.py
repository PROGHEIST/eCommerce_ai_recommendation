import os
import django
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Set the environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grocery_ai.grocery_ai.settings')

django.setup()

# Import Django models
from store.models import Order, Product, OrderItem  # ✅ Import OrderItem

def fetch_order_data():
    """Fetch order data from OrderItem instead of Order."""
    orders = OrderItem.objects.values('order__user_id', 'product_id', 'quantity', 'order__total_price', 'order__ordered_at')
    
    df = pd.DataFrame(orders)

    # Rename columns to maintain consistency
    df.rename(columns={'order__user_id': 'user_id', 'order__total_price': 'total_price', 'order__ordered_at': 'ordered_at'}, inplace=True)

    print(df.head())  # Display the first few rows
    return df

def clean_data(df):
    df.dropna(inplace=True)  # Remove missing values
    df['ordered_at'] = pd.to_datetime(df['ordered_at'])  # Convert dates
    df['user_id'] = df['user_id'].astype(int)
    df['product_id'] = df['product_id'].astype(int)
    df['quantity'] = df['quantity'].astype(int)
    df['total_price'] = df['total_price'].astype(float)
    return df

def get_user_product_matrix():
    """Generate the user-product matrix from OrderItem."""
    orders = OrderItem.objects.values('order__user_id', 'product_id', 'quantity')
    
    df = pd.DataFrame(orders)

    # Rename columns for clarity
    df.rename(columns={'order__user_id': 'user_id'}, inplace=True)

    # Check if the DataFrame is empty or missing 'quantity' column
    if df.empty:
        raise ValueError("No orders found in the database!")
    
    if 'quantity' not in df.columns:
        raise ValueError("Column 'quantity' is missing in the DataFrame!")

    # Pivot the data to create the user-product matrix
    user_product_matrix = df.pivot_table(index='user_id', columns='product_id', values='quantity', fill_value=0)
    
    return user_product_matrix

# Train KNN Model
def train_knn_model():
    matrix = get_user_product_matrix()
    model = NearestNeighbors(metric='cosine', algorithm='brute')
    model.fit(matrix)
    return model, matrix

def recommend_products(user_id, model, matrix, n_recommendations=5):
    """Recommend products based on KNN model."""
    if user_id not in matrix.index:
        return "User not found!"

    available_neighbors = len(matrix.index) - 1
    n_neighbors = min(n_recommendations + 1, available_neighbors)  # Ensure at least one neighbor is available

    if n_neighbors <= 0:
        return "Not enough data to generate recommendations."

    # Get nearest neighbors (excluding the user itself)
    distances, indices = model.kneighbors([matrix.loc[user_id]], n_neighbors=n_neighbors)
    
    # Get recommended product IDs
    recommended_product_ids = matrix.iloc[indices[0][1:]].sum(axis=0).sort_values(ascending=False).index[:n_recommendations]
    
    # Fetch recommended product names from the database
    recommended_products = Product.objects.filter(id__in=recommended_product_ids)
    return [product.name for product in recommended_products]

if __name__ == "__main__":
    df = fetch_order_data()
    df = clean_data(df)
    knn_model, user_product_matrix = train_knn_model()
    user_id = 1  # Change this to test different users

    try:
        matrix = get_user_product_matrix()
        print("User-Product Matrix:")
        print(matrix.head())  # Display the first few rows of the matrix
    except ValueError as e:
        print(e)

    recommendations = recommend_products(user_id, knn_model, user_product_matrix)
    print(f"Recommended products for user {user_id}: {recommendations}")
    print("Model trained successfully!")
    print(df.dtypes)  # Verify data types
