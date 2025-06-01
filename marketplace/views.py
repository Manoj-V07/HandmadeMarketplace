from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Review, Order, Category
from .forms import ProductForm, ReviewForm, ProductSearchForm, UserRegistrationForm
import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    # Get latest products
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get all categories with only necessary fields
    categories = Category.objects.only('id', 'name').all()
    
    # Get search form
    search_form = ProductSearchForm()
    
    context = {
        'products': products,
        'categories': categories,
        'search_form': search_form,
    }
    return render(request, 'marketplace/home.html', context)

def product_list(request):
    try:
        products = Product.objects.filter(is_active=True).select_related('category')
        search_form = ProductSearchForm(request.GET)
        
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            category = search_form.cleaned_data.get('category')
            min_price = search_form.cleaned_data.get('min_price')
            max_price = search_form.cleaned_data.get('max_price')
            
            if query:
                products = products.filter(
                    Q(name__icontains=query) | Q(description__icontains=query)
                )
            if category:
                products = products.filter(category=category)
            if min_price:
                products = products.filter(price__gte=min_price)
            if max_price:
                products = products.filter(price__lte=max_price)
        
        # Prefetch related data to avoid N+1 queries
        products = products.prefetch_related('reviews')
        
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        
        context = {
            'products': products,
            'search_form': search_form,
            'categories': Category.objects.all(),  # Add categories to context
        }
        return render(request, 'marketplace/product_list.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('marketplace:home')

def product_detail(request, pk, slug=None):
    try:
        product = get_object_or_404(Product, pk=pk, is_active=True)
        reviews = product.reviews.all().order_by('-created_at')
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product.pk)[:4]
        
        if request.method == 'POST' and request.user.is_authenticated:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been added.')
                return redirect('marketplace:product_detail', pk=product.pk)
        else:
            review_form = ReviewForm()
        
        return render(request, 'marketplace/product_detail.html', {
            'product': product,
            'reviews': reviews,
            'review_form': review_form,
            'related_products': related_products,
        })
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('marketplace:product_list')

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('marketplace:product_detail', pk=product.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    return render(request, 'marketplace/create_product.html', {
        'form': form,
        'categories': categories
    })

@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= product.stock:
            order = Order.objects.create(
                buyer=request.user,
                product=product,
                quantity=quantity,
                total_price=product.price * quantity
            )
            
            # Create Stripe payment intent
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_price * 100),  # Convert to cents
                    currency='usd',
                    metadata={'order_id': order.id}
                )
                return render(request, 'marketplace/payment.html', {
                    'order': order,
                    'client_secret': intent.client_secret
                })
            except Exception as e:
                messages.error(request, f'Payment error: {str(e)}')
                order.delete()
                return redirect('product_detail', pk=product_id)
        else:
            messages.error(request, 'Not enough stock available!')
    
    return render(request, 'marketplace/create_order.html', {'product': product})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'marketplace/register.html', {'form': form})

@login_required
def sell_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('marketplace:product_detail', pk=product.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    return render(request, 'marketplace/sell_product.html', {
        'form': form,
        'categories': categories
    })

@login_required
def cart(request):
    cart_items = request.session.get('cart', {})
    products = []
    total = Decimal('0.00')
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
            subtotal = product.price * quantity
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            # Remove invalid products from cart
            del cart_items[product_id]
    
    # Update session if any invalid products were removed
    if len(cart_items) != len(request.session.get('cart', {})):
        request.session['cart'] = cart_items
        request.session.modified = True
    
    return render(request, 'marketplace/cart.html', {
        'products': products,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = request.session.get('cart', {})
    
    # Convert product_id to string since session keys must be strings
    product_id = str(product_id)
    
    # Get quantity from form, default to 1 if not provided
    quantity = int(request.POST.get('quantity', 1))
    
    # Validate quantity
    if quantity < 1:
        quantity = 1
    if quantity > product.stock:
        messages.error(request, f'Only {product.stock} items available in stock.')
        return redirect('marketplace:product_detail', pk=product_id)
    
    if product_id in cart:
        # Check if adding the new quantity would exceed stock
        if cart[product_id] + quantity > product.stock:
            messages.error(request, f'Cannot add more items. Only {product.stock} items available in stock.')
            return redirect('marketplace:product_detail', pk=product_id)
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f'{quantity} {product.name} added to cart!')
    
    return redirect('marketplace:cart')

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart!')
    
    return redirect('marketplace:cart')

@login_required
def checkout(request):
    cart_items = request.session.get('cart', {})
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('marketplace:cart')
    
    products = []
    total = Decimal('0.00')
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
            if quantity > product.stock:
                messages.error(request, f'Not enough stock for {product.name}. Available: {product.stock}')
                return redirect('marketplace:cart')
            
            subtotal = product.price * quantity
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            messages.error(request, 'One or more products in your cart are no longer available.')
            return redirect('marketplace:cart')
    
    if request.method == 'POST':
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),  # Convert to cents
                currency='usd',
                metadata={'user_id': request.user.id}
            )
            
            # Create order
            order = Order.objects.create(
                buyer=request.user,
                total_amount=total,
                status='pending'
            )
            
            # Add order items
            for item in products:
                order.items.create(
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )
                # Update product stock
                item['product'].stock -= item['quantity']
                item['product'].save()
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            return render(request, 'marketplace/payment.html', {
                'order': order,
                'client_secret': intent.client_secret,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY
            })
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('marketplace:cart')
    
    return render(request, 'marketplace/checkout.html', {
        'products': products,
        'total': total
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    return render(request, 'marketplace/order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    return render(request, 'marketplace/order_detail.html', {
        'order': order
    })

@login_required
def profile(request):
    # Get user's products
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    # Get user's orders
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    
    # Get user's reviews
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'products': products,
        'orders': orders,
        'reviews': reviews,
    }
    return render(request, 'marketplace/profile.html', context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    
    if order.status == 'pending':
        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'Only pending orders can be cancelled.')
    
    return redirect('marketplace:order_detail', order_id=order.id)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Get the current user
        user = request.user
        
        # Update user information
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Save changes
        user.save()
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('marketplace:profile')
    
    return render(request, 'marketplace/edit_profile.html', {
        'user': request.user
    })

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been added successfully!')
            return redirect('marketplace:product_detail', pk=product.pk)
    else:
        form = ReviewForm()
    
    return render(request, 'marketplace/add_review.html', {
        'form': form,
        'product': product
    })

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    # Check if the user is the seller of the product
    if request.user != product.seller:
        messages.error(request, 'You do not have permission to edit this product.')
        return redirect('marketplace:product_detail', pk=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('marketplace:product_detail', pk=product.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    categories = Category.objects.all()
    return render(request, 'marketplace/edit_product.html', {
        'form': form,
        'product': product,
        'categories': categories
    }) 