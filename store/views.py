from django.shortcuts import get_object_or_404, render, redirect
from .models import Order, Product, OrderItem
from .data_preprocessing import train_knn_model, recommend_products
from .recommendation import recommend_similar_products
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
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
    featured_products = Product.objects.all()[:8]
    context = {
        'featured_products': featured_products,
        'user': request.user
    }
    return render(request, 'store/home.html', context)

def user_recommendations(request, user_id):
    recommendations = recommend_products(user_id, knn_model, user_product_matrix)
    print(f"User {user_id} recommendations: {recommendations}")
    recommended_products = Product.objects.filter(name__in=recommendations)
    print(f"Filtered products: {recommended_products}")

    return render(request, 'store/user_recommendations.html', {'recommended_products': recommended_products})

def product_recommendations(request, product_id):
    recommendations = recommend_similar_products(product_id)
    recommended_products = Product.objects.filter(name__in=recommendations)
    return render(request, 'store/product_recommendations.html', {'recommended_products': recommended_products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    recommendations = recommend_similar_products(product_id)
    recommended_products = Product.objects.filter(name__in=recommendations)

    return render(request, 'store/product_detail.html', {'product': product, 'recommended_products': recommended_products})


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

            messages.success(request, "Payment successful! Order placed.")
            return redirect("order_history")  # Redirect to order history

        except Exception as e:
            messages.error(request, f"Error processing order: {str(e)}")
            return redirect("checkout")

    return redirect("home")


def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders.html', {'orders': orders})


