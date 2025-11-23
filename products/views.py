from products.models import Category, Product, CartItem, DeliveryAddress, Order
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
# import qrcode
from django.db.models import Count, Q
from .forms import *


# @login_required(login_url='login')
def homepage(request):
    products = Product.objects.all()
    recommended_products = []
    rv_ids = request.session.get('recently_viewed', [])
    if rv_ids:
        cats = list(Product.objects.filter(id__in=rv_ids).values_list('category_id', flat=True))
        recommended_products = list(Product.objects.filter(category_id__in=cats).exclude(id__in=rv_ids).order_by('-created_at')[:5])
    else:
        recommended_products = list(Product.objects.order_by('-created_at')[:5])
    
    # Get trending products (newly launched)
    trending_products = list(Product.objects.order_by('-created_at')[:5])
    
    # Get products by category
    categories = Category.objects.all()
    products_by_category = {}
    for category_obj in categories:
        products_by_category[category_obj] = Product.objects.filter(category=category_obj)[:8]  # Limit to 8 items per category
    
    return render(request, 'products/home.html', {
        'products': products, 
        'recommended_products': recommended_products,
        'trending_products': trending_products,
        'products_by_category': products_by_category
    })


def products(request):
    return render(request, 'products/products.html')


@login_required(login_url='login')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'products/cart.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # Track recently viewed in session (max 10)
    rv = request.session.get('recently_viewed', [])
    if product.id not in rv:
        rv.insert(0, product.id)
        rv = rv[:10]
    request.session['recently_viewed'] = rv
    
    # Get additional images (image2 and image3 if they exist)
    additional_images = product.get_additional_images()
    
    # Get products from the same category (excluding current product)
    same_category_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:8]
    
    return render(request, 'products/detail.html', {
        'product': product,
        'additional_images': additional_images,
        'same_category_products': same_category_products,
    })


def category(request):
    from django.db.models import Count
    
    categories = Category.objects.all()
    
    # Track search query in session for recommendation algorithm
    search_query = request.GET.get('q', '').strip()
    if search_query:
        search_history = request.session.get('search_history', [])
        if search_query not in search_history:
            search_history.insert(0, search_query)
            search_history = search_history[:20]  # Keep last 20 searches
        request.session['search_history'] = search_history
    
    # Get selected category
    category_id = request.GET.get('category')
    selected_category = None
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            selected_category = None
    
    # Get filter parameters (all optional)
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort = request.GET.get('sort', '').strip()
    
    # Start with base queryset
    all_products = Product.objects.all()
    
    # Apply search query filter if provided
    if search_query:
        all_products = all_products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    
    # Apply category filter if selected
    if selected_category:
        all_products = all_products.filter(category=selected_category)
    
    # Apply price filters (optional)
    if min_price:
        try:
            all_products = all_products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            all_products = all_products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Apply sorting (order_by must be before slicing)
    if sort == 'price_asc':
        all_products = all_products.order_by('price')
    elif sort == 'price_desc':
        all_products = all_products.order_by('-price')
    elif sort == 'newest':
        all_products = all_products.order_by('-created_at')
    elif sort == 'popular':
        all_products = all_products.annotate(popularity=Count('cartitem')).order_by('-popularity')
    else:
        # Default: newest first
        all_products = all_products.order_by('-created_at')
    
    # Get user behavior data for recommendations
    rv_ids = request.session.get('recently_viewed', [])
    search_history = request.session.get('search_history', [])
    
    # Get user's cart and order history if logged in
    user_interested_categories = []
    user_interested_products = []
    
    if request.user.is_authenticated:
        # Get categories from user's cart items
        cart_category_ids = CartItem.objects.filter(user=request.user).values_list('product__category_id', flat=True).distinct()
        user_interested_categories.extend(cart_category_ids)
        
        # Get product IDs from cart items for personalized recommendations
        cart_product_ids = CartItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        user_interested_products.extend(cart_product_ids)
    
    # Add categories from recently viewed products
    if rv_ids:
        rv_categories = Product.objects.filter(id__in=rv_ids).values_list('category_id', flat=True).distinct()
        user_interested_categories.extend(rv_categories)
    
    # Add categories from search history (analyze search terms)
    if search_history:
        for query in search_history[:5]:  # Use top 5 recent searches
            matching_products = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )[:5]
            for product in matching_products:
                if product.category_id not in user_interested_categories:
                    user_interested_categories.append(product.category_id)
    
    # Smart recommendation: 10 items from selected category based on user interest
    recommended_category_products = []
    next_category = None
    
    if selected_category:
        # Get 10 products from selected category based on user behavior
        base_query = Product.objects.filter(category=selected_category)
        
        # Prioritize products similar to user's interests
        if user_interested_categories:
            # Boost products from categories user has interacted with
            recommended_category_products = list(
                base_query.annotate(
                    popularity=Count('cartitem')
                ).order_by('-popularity', '-created_at')[:10]
            )
        else:
            # If no history, show popular products in the category
            recommended_category_products = list(
                base_query.annotate(
                    popularity=Count('cartitem')
                ).order_by('-popularity', '-created_at')[:10]
            )
        
        # Get next category (alphabetically or by popularity)
        next_categories = Category.objects.exclude(id=selected_category.id).order_by('name')
        if next_categories.exists():
            next_category = next_categories.first()
    
    # Personalized recommendations: 10 latest items based on search history and behavior
    personalized_products = []
    
    if user_interested_categories or search_history or rv_ids:
        # Get products from user's interested categories
        personalized_query = Product.objects.filter(
            category_id__in=list(set(user_interested_categories))
        ).annotate(
            popularity=Count('cartitem')
        ).order_by('-created_at', '-popularity')
        
        # Exclude already viewed products
        if rv_ids:
            personalized_query = personalized_query.exclude(id__in=rv_ids)
        
        personalized_products = list(personalized_query[:10])
    
    # If no personalized products, show latest products
    if not personalized_products:
        personalized_products = list(Product.objects.order_by('-created_at')[:10])
    
    # Get products by category for display (when no category is selected)
    products_by_category = {}
    if not selected_category:
        for category_obj in categories:
            category_products = Product.objects.filter(category=category_obj).order_by('-created_at')[:8]
            products_by_category[category_obj] = category_products
    
    return render(request, 'products/category.html', {
        'categories': categories,
        'selected_category': selected_category,
        'all_products': all_products,
        'recommended_category_products': recommended_category_products,
        'next_category': next_category,
        'personalized_products': personalized_products,
        'products_by_category': products_by_category,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'query': search_query,
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = request.POST.get('quantity', 1)
    quantity = int(quantity) if int(quantity) > 0 else 1

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart')


@login_required(login_url='login')
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    qr_code_path = f"{settings.MEDIA_URL}qr_codes/order_payment_qr.png"
    
    # Get user's default delivery address or the most recent one
    default_address = DeliveryAddress.objects.filter(user=request.user, is_default=True).first()
    if not default_address:
        # If no default, get the most recently used address
        default_address = DeliveryAddress.objects.filter(user=request.user).order_by('-created_at').first()
    
    # Initialize forms with default address if exists
    delivery_form = DeliveryAddressForm(instance=default_address) if default_address else DeliveryAddressForm()
    form = DeliveryForm()

    if request.method == "POST":
        # Check if user wants to proceed to payment
        if 'proceed_to_payment' in request.POST:
            delivery_form = DeliveryAddressForm(request.POST)
            if delivery_form.is_valid():
                # Always keep a single address per user: update if exists, otherwise create
                existing = DeliveryAddress.objects.filter(user=request.user).order_by('-updated_at').first()
                if existing:
                    for field, value in delivery_form.cleaned_data.items():
                        setattr(existing, field, value)
                    existing.save()
                    delivery_address = existing
                else:
                    delivery_address = delivery_form.save(commit=False)
                    delivery_address.user = request.user
                    delivery_address.save()
                
                # Store the delivery address ID in session for the payment page
                request.session['delivery_address_id'] = delivery_address.id
                
                # Redirect to payment page
                return redirect('payment')
        else:
            # Original order submission with payment proof
            form = DeliveryForm(request.POST, request.FILES)
            if form.is_valid():
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = total_price
                order.payment_proof = request.FILES.get('payment_proof')
                order.save()

                cart_items.delete()
                return render(request, 'products/checkout_success.html', {'order': order, 'qr_code_path': qr_code_path})

    context = {
        'delivery_form': delivery_form,
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'qr_code_path': qr_code_path,
        'default_address': default_address,
    }
    return render(request, 'products/checkout.html', context)


@login_required(login_url='login')
def payment(request):
    # Get delivery address from session
    delivery_address_id = request.session.get('delivery_address_id')
    if not delivery_address_id:
        messages.error(request, "Please fill in delivery information first.")
        return redirect('checkout')
    
    delivery_address = get_object_or_404(DeliveryAddress, id=delivery_address_id, user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    qr_code_path = f"{settings.MEDIA_URL}qr_codes/order_payment_qr.png"

    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'qr':
            # Handle QR code payment with proof upload
            payment_proof = request.FILES.get('payment_proof')
            if payment_proof:
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    delivery_address=f"{delivery_address.full_name}, {delivery_address.street_address}, {delivery_address.location}, {delivery_address.district}, {delivery_address.province}",
                    phone_number=delivery_address.phone_number,
                    total_price=total_price,
                    payment_proof=payment_proof,
                    payment_status='Pending',
                    status='Pending'
                )
                cart_items.delete()
                # Clear session
                del request.session['delivery_address_id']
                return redirect('checkout_success', order_id=order.id)
            else:
                messages.error(request, "Please upload payment proof.")
        
        elif payment_method == 'khalti':
            # Initiate Khalti payment using new API
            url = "https://a.khalti.com/api/v2/epayment/initiate/"
            
            return_url = request.build_absolute_uri('/khalti/verify/')
            website_url = request.build_absolute_uri('/')
            
            payload = {
                "return_url": return_url,
                "website_url": website_url,
                "amount": int(total_price * 100),  # Convert to paisa
                "purchase_order_id": f"order_{delivery_address_id}_{request.user.id}",
                "purchase_order_name": "Product Order",
                "customer_info": {
                    "name": delivery_address.full_name,
                    "email": request.user.email if hasattr(request.user, 'email') else "customer@example.com",
                    "phone": delivery_address.phone_number
                }
            }
            
            headers = {
                "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                response_data = response.json()
                
                if response.status_code == 200 and 'payment_url' in response_data:
                    # Store pidx in session for verification
                    request.session['khalti_pidx'] = response_data['pidx']
                    # Redirect to Khalti payment page
                    return redirect(response_data['payment_url'])
                else:
                    messages.error(request, f"Payment initiation failed: {response_data.get('detail', 'Unknown error')}")
            except Exception as e:
                messages.error(request, f"Payment error: {str(e)}")
    
    context = {
        'delivery_address': delivery_address,
        'cart_items': cart_items,
        'total_price': total_price,
        'qr_code_path': qr_code_path,
    }
    return render(request, 'products/payment.html', context)


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')


def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == "POST":
        action = request.POST.get('action')
        if action == "increase":
            item.quantity += 1
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1
        item.save()
    return redirect('cart')


@login_required(login_url='login')
def checkout_success(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('cart')

    context = {
        'order': order,
        'qr_code_path': f"{settings.MEDIA_URL}qr_codes/order_{order.id}.png",
    }
    return render(request, 'products/checkout_success.html', context)


@csrf_exempt
@login_required(login_url='login')
def khalti_verify(request):
    # This endpoint is called when user returns from Khalti payment page
    pidx = request.GET.get('pidx')
    
    if not pidx:
        messages.error(request, "Invalid payment response")
        return redirect('payment')
    
    # Verify payment with Khalti
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    
    payload = {
        "pidx": pidx
    }
    
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('status') == 'Completed':
            # Payment verified successfully
            delivery_address_id = request.session.get('delivery_address_id')
            
            if delivery_address_id:
                delivery_address = DeliveryAddress.objects.get(id=delivery_address_id, user=request.user)
                cart_items = CartItem.objects.filter(user=request.user)
                total_price = sum(item.product.price * item.quantity for item in cart_items)
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    delivery_address=f"{delivery_address.full_name}, {delivery_address.street_address}, {delivery_address.location}, {delivery_address.district}, {delivery_address.province}",
                    phone_number=delivery_address.phone_number,
                    total_price=total_price,
                    payment_status='Paid',
                    status='Order Confirmed'
                )
                
                # Clear cart and session
                cart_items.delete()
                if 'delivery_address_id' in request.session:
                    del request.session['delivery_address_id']
                if 'khalti_pidx' in request.session:
                    del request.session['khalti_pidx']
                
                messages.success(request, "Payment successful! Your order has been placed.")
                return redirect('checkout_success', order_id=order.id)
            else:
                messages.error(request, "Delivery address not found")
                return redirect('checkout')
        else:
            messages.error(request, f"Payment verification failed: {response_data.get('status', 'Unknown')}")
            return redirect('payment')
            
    except Exception as e:
        messages.error(request, f"Payment verification error: {str(e)}")
        return redirect('payment')

# Search results page
def search(request):
    q = request.GET.get('q', '').strip()
    
    # Track search query in session for recommendation algorithm
    if q:
        search_history = request.session.get('search_history', [])
        if q not in search_history:
            search_history.insert(0, q)
            search_history = search_history[:20]  # Keep last 20 searches
        request.session['search_history'] = search_history
    
    categories = Category.objects.all()
    products = Product.objects.all()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'popular':
        products = products.annotate(popularity=Count('cartitem')).order_by('-popularity')
    else:
        products = products.order_by('-created_at')
    
    return render(request, 'products/category.html', {
        'categories': categories,
        'all_products': products,
        'query': q,
        'sort': sort,
    })

# Typeahead suggestions JSON
def search_suggestions(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        qs = Product.objects.filter(name__icontains=q)[:8]
        for p in qs:
            results.append({
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'image': p.image.url if p.image else ''
            })
    return JsonResponse({'results': results})
