from django.urls import path
from .views import homepage, user_signup, user_login,dashboard, user_logout,cancel_order,track_order,filter_products, add_to_cart, view_cart, remove_from_cart, checkout, payment_success, order_history, recommended_products_view, product_detail, contact_view, search_suggestions
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', homepage, name='homepage'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path("search-suggestions/", search_suggestions, name="search_suggestions"),
    path('contact-us/', contact_view, name="contact"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("recommendations/", recommended_products_view, name="recommendations"),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment-success/', payment_success, name='payment_success'),
    path("orders/", order_history, name="order_history"),
    path("dashboard/", dashboard, name="dashboard"),
    path('signup/', user_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('track/<str:tracking_number>/', track_order, name='track_order'),
    path('filter_products/', filter_products, name='filter_products'),
    path("cancel_order/<int:order_id>/", cancel_order, name="cancel_order"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)