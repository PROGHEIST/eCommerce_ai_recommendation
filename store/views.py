from django.shortcuts import get_object_or_404, render, redirect
from .models import Order, Product, OrderItem, Recommendation, ProductVisit
from .data_preprocessing import train_knn_model, recommend_products
from .models import Recommendation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


import urllib.parse
import qrcode
from io import BytesIO
from django.http import HttpResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal


knn_model, user_product_matrix = train_knn_model()

def homepage(request):
    featured_products = Product.objects.all()[:8]  # Fetch featured products

    recommended_products = []
    if request.user.is_authenticated:
        recommendation = Recommendation.objects.filter(user=request.user).first()
        if recommendation:
            recommended_products = recommendation.recommended_products.all()[:8]  # Fetch recommendations

    context = {
        'featured_products': featured_products,
        'recommended_products': recommended_products,
        'user': request.user
    }
    return render(request, 'store/home.html', context)


def recommended_products_view(request):
    # First, get recommendations based on the user's previous product visits
    recommendations_based_on_visits = recommend_products_based_on_visits(request)
    
    # Get static recommendations (if any) from the Recommendation model
    recommendations = Recommendation.objects.filter(user=request.user).first()

    recommended_products = []
    
    if recommendations:
        # Fetch the recommended products associated with the recommendation
        recommended_products += list(recommendations.recommended_products.all())
    
    # Now combine with the dynamic recommendations from visits (to avoid duplicates)
    if recommendations_based_on_visits:
        recommended_products += recommendations_based_on_visits

    # Remove duplicates from the list
    recommended_products = list(set(recommended_products))

    # Optionally, filter recommended products by categories
    ordered_categories = OrderItem.objects.filter(order__user=request.user).values_list('product__category', flat=True)
    recommended_products = [product for product in recommended_products if product.category in ordered_categories]

    # Render the recommendations page with the recommended products
    return render(request, "recommendations.html", {"recommended_products": recommended_products})


def recommend_products_based_on_visits(request):
    # Get the current time and calculate the time window (e.g., 7 days ago)
    now = timezone.now()
    time_threshold = now - timedelta(days=7)  # 7 days ago
    
    # Fetch products that the user has visited more than or equal to 2 times in the last 7 days
    visited_products = ProductVisit.objects.filter(
        user=request.user,
        visit_count__gte=2,  # Threshold for visits (e.g., 2 visits)
        last_visited__gte=time_threshold  # Time frame (7 days ago)
    )

    # Get the categories of those products
    categories = visited_products.values_list('product__category', flat=True)
    
    # Get all products from those categories (excluding the ones already visited)
    recommended_products = Product.objects.filter(category__in=categories).exclude(
        id__in=visited_products.values_list('product', flat=True))

    return recommended_products


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the user has already visited this product
    product_visit, created = ProductVisit.objects.get_or_create(user=request.user, product=product)
    
    if created:
        product_visit.visit_count = 1  # First visit
    else:
        product_visit.visit_count += 1  # Increment the visit count
        
    # Save the visit record
    product_visit.save()
    
    return render(request, "store/product_detail.html", {"product": product})


def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully! You can log in now.")
        return redirect('login')

    return render(request, 'accounts/signup.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('homepage')  # Change 'home' to your homepage URL name
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.image.url
        }
    
    
    request.session['cart'] = cart
    request.session.modified = True 
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'view_cart'))

def view_cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())

    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Item removed from cart.")

    return redirect('view_cart')



def checkout(request):
    cart = request.session.get('cart', {})
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())

    if not cart:
        return render(request, 'cart.html', {"cart": cart})

    # Create Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    order_data = {
        "amount": int(total_price * 100),
        "currency": "INR",
        "payment_capture": 1
    }

    order = client.order.create(order_data)

    return render(request, 'checkout.html', {
        'cart': cart,
        'total_price': total_price,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'order_id': order['id']
    })




# Add a function to update or create recommendations based on the products ordered
def update_recommendations(user):
    # Fetch the products ordered by the user
    ordered_products = OrderItem.objects.filter(order__user=user).values_list('product__name', flat=True)

    # Create or get the user's recommendations
    recommendation, created = Recommendation.objects.get_or_create(user=user)

    # Add related products to the recommendation (Here, we're adding products based on name similarity for simplicity)
    for product_name in ordered_products:
        related_products = Product.objects.filter(name__icontains=product_name)  # You can filter based on categories, etc.
        recommendation.recommended_products.add(*related_products)

    recommendation.save()
    
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            data = request.POST
            print("Payment Success Data:", data)  # Debugging

            # ✅ Retrieve cart, user, address, and phone number
            cart = request.session.get('cart', {})
            user = request.user
            address = request.POST.get("address")
            phone = request.POST.get("phone")

            if not cart:
                messages.error(request, "Cart is empty. Cannot place order.")
                return redirect("cart")

            # ✅ Create an Order object
            total_price = sum(float(item["price"]) * item["quantity"] for item in cart.values())
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                address=address,
                phone=phone
            )

            # ✅ Save each item in the OrderItem model
            for key, item in cart.items():
                product = Product.objects.get(id=key)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"],
                    price=float(item["price"]),
                )

            # ✅ Clear the cart after saving the order
            request.session["cart"] = {}

            # ✅ Update the user's recommendations
            update_recommendations(user)

            messages.success(request, "Payment successful! Order placed.")
            return redirect("order_history")  # Redirect to order history

        except Exception as e:
            messages.error(request, f"Error processing order: {str(e)}")
            return redirect("checkout")

    return redirect("home")


def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-ordered_at')
    return render(request, 'orders.html', {'orders': orders})


