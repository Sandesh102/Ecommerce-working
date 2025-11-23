from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('category/', views.category, name='category'),
    path('cart/', views.cart, name='cart'),
    path('product/<slug:slug>/', views.detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/',views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('khalti/verify/', views.khalti_verify, name='khalti_verify'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    path('products/', views.products, name='products'),
    path('search/', views.search, name='search'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('help/', TemplateView.as_view(template_name='products/help.html'), name='help'),
    path('privacy/', TemplateView.as_view(template_name='products/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='products/terms.html'), name='terms'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
