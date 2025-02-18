import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from store.models import Product

# Fetch product data
def get_product_data():
    products = Product.objects.all().values('id', 'name', 'category', 'description')
    df = pd.DataFrame(products)
    df['features'] = df['category'] + " " + df['description']
    return df

# Train TF-IDF model
def train_tfidf_model():
    df = get_product_data()
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['features'])
    return tfidf_matrix, df

# Recommend similar products based on text similarity
def recommend_similar_products(product_id, n_recommendations=5):
    tfidf_matrix, df = train_tfidf_model()
    
    product_index = df[df['id'] == product_id].index[0]
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    similar_indices = cosine_sim[product_index].argsort()[-(n_recommendations+1):-1][::-1]
    recommended_products = df.iloc[similar_indices]['name'].tolist()
    
    return recommended_products

if __name__ == "__main__":
    product_id = 1  # Change this to test different products
    recommendations = recommend_similar_products(product_id)
    print(f"Similar products to {product_id}: {recommendations}")
