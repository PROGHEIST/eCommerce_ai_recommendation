from django.urls import path
from .views import user_recommendations, product_recommendations, product_detail, homepage, user_signup, user_login, user_logout, add_to_cart, view_cart, remove_from_cart, checkout, payment_success, order_history
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', homepage, name='homepage'),
    path('recommend/user/<int:user_id>/', user_recommendations, name='user_recommendations'),
    path('recommend/product/<int:product_id>/', product_recommendations, name='product_recommendations'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment-success/', payment_success, name='payment_success'),
    path("orders/", order_history, name="order_history"),
    path('signup/', user_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)