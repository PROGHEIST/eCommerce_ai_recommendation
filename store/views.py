from django.shortcuts import get_object_or_404, render, redirect
from .models import Order, Product, OrderItem, Recommendation, ProductVisit, ProductReview, ContactMessage
from .data_preprocessing import train_knn_model, recommend_products
from .models import Recommendation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
import urllib.parse
from .forms import ProductReviewForm
import math
import qrcode
from io import BytesIO
from django.http import HttpResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib.auth.models import AnonymousUser

from .recommendations import generate_recommendations

knn_model, user_product_matrix = train_knn_model()

def homepage(request):
    category = request.GET.get('category', 'all')

    recently_visited = []

    if request.user.is_authenticated:
        recently_visited = ProductVisit.objects.filter(user=request.user).order_by('-last_visited')[:8]

    if category == 'all':
        featured_products = Product.objects.all()
        import math
        for items in featured_products:
            discount_price = items.market_price - items.selling_price
            discount_percent = math.floor((discount_price / items.market_price) * 100)
            items.discount_percent = discount_percent


    else:
        featured_products = Product.objects.filter(category=category)
    
    recommended_products = []
    if request.user.is_authenticated:
        recommended_products = generate_recommendations(request.user)[:8] 

    context = {
        'featured_products': featured_products,
        'discount_percent': discount_percent,
        'recommended_products': recommended_products,
        'recently_visited': recently_visited,
        'user': request.user,
        'current_category': category,
    }
    return render(request, 'store/home.html', context)



def filter_products(request):
    category = request.GET.get('category', 'all')
    if category == 'all':
        products = Product.objects.all()
    else:
        products = Product.objects.filter(category=category)

    html = render_to_string('store/product_list.html', {'products': products})
    return JsonResponse(html, safe=False)

def recommended_products_view(request):
    recommended_products = []
    if request.user.is_authenticated:
        recommended_products = generate_recommendations(request.user)

    return render(request, "recommendations.html", {"recommended_products": recommended_products})


def recommend_products_based_on_visits(request):
    
    now = timezone.now()
    time_threshold = now - timedelta(days=7)  
    
    
    visited_products = ProductVisit.objects.filter(
        user=request.user,
        visit_count__gte=2,  
        last_visited__gte=time_threshold  
    )

    
    categories = visited_products.values_list('product__category', flat=True)
    
    
    recommended_products = Product.objects.filter(category__in=categories).exclude(
        id__in=visited_products.values_list('product', flat=True))

    return recommended_products




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    product_visit, created = ProductVisit.objects.get_or_create(user=request.user, product=product)

    
    discount_price = product.market_price - product.selling_price
    discount_percent = math.floor((discount_price / product.market_price) * 100)
    product.discount_percent = discount_percent

    for item in similar_products:
        discount_price = item.market_price - item.selling_price
        discount_percent = math.floor((discount_price / item.market_price) * 100)
        item.discount_percent = discount_percent

    
    if created:
        product_visit.visit_count = 1 
    else:
        product_visit.visit_count += 1
    product_visit.save()

    
    existing_review = ProductReview.objects.filter(product=product, user=request.user).first()
    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm(instance=existing_review)

    context = {
        "product": product,
        "similar_products": similar_products,
        "discount_percent": discount_percent,
        "form": form,
        "reviews": product.reviews.all().order_by('-created_at'),
        "average_rating": product.average_rating(),
    }

    return render(request, "store/product_detail.html", context)



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
    quantity = int(request.POST.get('quantity', 1))  # Get quantity from form, default to 1

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'selling_price': str(product.selling_price),
            'quantity': quantity,
            'image': product.image.url
        }

    request.session['cart'] = cart
    request.session.modified = True 

    messages.success(request, f"{product.name} added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'view_cart'))

def view_cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(float(item['selling_price']) * item['quantity'] for item in cart.values())

    if request.user.is_authenticated:
        recently_visited = ProductVisit.objects.filter(user=request.user)[:8]
    
    context = {
        'cart': cart, 
        'total_price': total_price,
        'recently_visited': recently_visited
    }
    return render(request, 'cart.html', context)




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
    total_price = sum(float(item['selling_price']) * item['quantity'] for item in cart.values())

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




def update_recommendations(user):
    ordered_products = OrderItem.objects.filter(order__user=user).values_list('product__name', flat=True)
    recommendation, created = Recommendation.objects.get_or_create(user=user)

    for product_name in ordered_products:
        related_products = Product.objects.filter(name__icontains=product_name)  # You can filter based on categories, etc.
        recommendation.recommended_products.add(*related_products)

    recommendation.save()


from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib import messages
from .models import Order, OrderItem, Product
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            data = request.POST
            print("Payment Success Data:", data)

            cart = request.session.get('cart', {})
            user = request.user
            address = request.POST.get("address")
            phone = request.POST.get("phone")
            upi_id = request.POST.get("upi_id")

            if not cart:
                messages.error(request, "Cart is empty. Cannot place order.")
                return redirect("cart")

            if not address or not phone:
                messages.error(request, "Address and phone number are required.")
                return redirect("checkout")

            total_price = sum(float(item["selling_price"]) * item["quantity"] for item in cart.values())
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                address=address,
                phone=phone,
                upi_id=upi_id
            )

            for key, item in cart.items():
                try:
                    product = Product.objects.get(id=key)

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item["quantity"],
                        price=float(item["selling_price"]),
                    )
                except Product.DoesNotExist:
                    messages.error(request, f"Product with ID {key} not found. Please try again.")
                    return redirect("cart")

            request.session["cart"] = {}  # Clear cart after successful order

            update_recommendations(user)  # AI-based recommendations update

            messages.success(request, "Payment successful! Order placed.")
            return redirect("order_history")

        except Exception as e:
            logger.error(f"Error processing order: {str(e)}", exc_info=True)
            messages.error(request, "An error occurred while processing your payment. Please try again.")
            return redirect("checkout")

    return redirect("home")



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Restrict cancellation for "Out for Delivery" or "Delivered" status
    if order.status in ["out_for_delivery", "delivered"]:
        messages.error(request, "You cannot cancel an order that is Out for Delivery or Delivered.")
        return redirect("order_history")

    if request.method == "POST":
        cancel_reason = request.POST.get("cancel_reason", "").strip()

        if not cancel_reason:
            messages.error(request, "Please provide a reason for cancellation.")
            return redirect("cancel_order", order_id=order.id)

        order.status = "cancelled"
        order.cancel_reason = cancel_reason
        order.save()

        messages.success(request, "Your order has been cancelled successfully.")
        return redirect("order_history")

    return render(request, "cancel_order.html", {"order": order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-ordered_at')

    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'orders.html', {'orders': orders})


def track_order(request, tracking_number):
    order = get_object_or_404(Order, tracking_number=tracking_number)
    return render(request, 'track_order.html', {'order': order})

def dashboard(request):
    # Fetch the user's orders
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')

    # Fetch the user's product visits
    product_visits = ProductVisit.objects.filter(user=request.user).order_by('-last_visited')

    # Fetch the user's recommendations
    recommendations = Recommendation.objects.filter(user=request.user).first()

    context = {
        'orders': orders,
        'product_visits': product_visits,
        'recommendations': recommendations.recommended_products.all() if recommendations else [],
    }
    return render(request, 'dashboard.html', context)




def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')


        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        send_mail(
            subject=f"New Contact Message: {subject}",
            message=f"From: {name} <{email}>\n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')

    return render(request, 'contact.html')



def search_suggestions(request):
    term = request.GET.get("term", "")
    products = Product.objects.filter(name__icontains=term)
    suggestions = [
        {"label": product.name, "value": product.name, "id": product.id}
        for product in products
    ]
    return JsonResponse(suggestions, safe=False)
