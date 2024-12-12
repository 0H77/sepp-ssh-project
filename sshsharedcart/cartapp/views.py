from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupFormStep1, SignupFormStep2
from .models import Product, Cart, CartItem, Supermarket
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    logger.info('Accessed home view')
    try:
        return render(request, 'home.html')
    except Exception as e:
        logger.error(f'Error in home view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})

def login_view(request):
    logger.info('Accessed login view')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.debug(f'Login attempt for user: {username}')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f'User logged in: {username}')
            return redirect('home')
        else:
            logger.warning(f'Failed login attempt for user: {username}')
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logger.info(f'User logged out: {request.user.username}')
    logout(request)
    return redirect('home')

def signup(request):
    logger.info('Accessed signup view')
    if request.method == 'POST':
        form = SignupFormStep1(request.POST)
        if form.is_valid():
            request.session['signup_email'] = form.cleaned_data['email']
            return redirect('signup_step2')
        else:
            logger.warning('Signup form invalid')
    else:
        form = SignupFormStep1()
    return render(request, 'registration/signup.html', {'form': form})

def signup_step2(request):
    logger.info('Accessed signup_step2 view')
    if 'signup_email' not in request.session:
        logger.warning('Signup step2 accessed without signup_step1')
        return redirect('signup')
    if request.method == 'POST':
        form = SignupFormStep2(request.POST)
        if form.is_valid():
            email = request.session.pop('signup_email')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            user = User.objects.create_user(username=username, email=email, password=password)
            user.profile.address = address
            user.profile.save()
            logger.info(f'Profile created for user: {username}')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('supermarkets')
        else:
            logger.warning('Signup step2 form invalid')
    else:
        form = SignupFormStep2()
    return render(request, 'registration/signup_step2.html', {'form': form})

@login_required(login_url='login')
def supermarkets(request):
    logger.info('Accessed supermarkets view')
    try:
        supermarkets = Supermarket.objects.all()
        selected_supermarket_id = request.GET.get('supermarket')
        search_query = request.GET.get('search', '')

        products = Product.objects.all()
        if selected_supermarket_id:
            products = products.filter(supermarket__id=selected_supermarket_id)
            logger.debug(f'Filtered products by supermarket ID: {selected_supermarket_id}')
        if search_query:
            products = products.filter(name__icontains=search_query)
            logger.debug(f'Search query applied: {search_query}')

        context = {
            'supermarkets': supermarkets,
            'products': products,
            'selected_supermarket_id': selected_supermarket_id,
            'search_query': search_query,
        }
        return render(request, 'supermarkets.html', context)
    except Exception as e:
        logger.error(f'Error in supermarkets view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})

@login_required(login_url='login')
def shared_cart(request):
    logger.info('Accessed shared_cart view')
    try:
        cart, created = Cart.objects.get_or_create(name='Shared Cart')
        cart.users.add(request.user)
        total_price = sum(item.total_price for item in cart.items.all())
        context = {'cart': cart, 'total_price': total_price}
        return render(request, 'shared_cart.html', context)
    except Exception as e:
        logger.error(f'Error in shared_cart view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})

@login_required(login_url='login')
def add_to_cart(request, product_id):
    logger.info('Accessed add_to_cart view')
    try:
        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(name='Shared Cart')
        cart.users.add(request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            added_by=request.user,  # Assign to the current user
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'Added {product.name} to cart.')
        
        next_url = request.POST.get('next', 'supermarkets')
        return redirect(next_url)
    except Exception as e:
        logger.error(f'Error in add_to_cart view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})

@login_required(login_url='login')
def update_quantity(request, item_id):
    logger.info('Accessed update_quantity view')
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        if cart_item.added_by != request.user:
            messages.error(request, "You can only update items you added.")
            return redirect('shared_cart')
        if request.method == 'POST':
            quantity = request.POST.get('quantity')
            if quantity:
                cart_item.quantity = int(quantity)
                cart_item.save()
        return redirect('shared_cart')
    except Exception as e:
        logger.error(f'Error in update_quantity view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    logger.info('Accessed remove_from_cart view')
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()
        return redirect('shared_cart')
    except Exception as e:
        logger.error(f'Error in remove_from_cart view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})

@login_required(login_url='login')
def checkout(request):
    logger.info('Accessed checkout view')
    try: 
        cart, created = Cart.objects.get_or_create(name='Shared Cart')
        cart.users.add(request.user)
        cart_items = cart.items.select_related('product', 'added_by').all()

        user_totals = {}
        user_counts = {}
        for item in cart_items:
            username = item.added_by.username
            user_totals[username] = user_totals.get(username, 0) + item.quantity * item.product.price
            user_counts[username] = user_counts.get(username, 0) + item.quantity

        user_data = [
            {'username': username, 'count': count, 'total': user_totals[username]}
            for username, count in user_counts.items()
        ]

        product_data = defaultdict(lambda: {'product': None, 'users': [], 'total_quantity': 0})
        for item in cart_items:
            product = item.product
            if not product_data[product]['product']:
                product_data[product]['product'] = product
            product_data[product]['users'].append({
                'username': item.added_by.username,
                'quantity': item.quantity
            })
            product_data[product]['total_quantity'] += item.quantity

        product_data = list(product_data.values())

        total_price = sum(user_totals.values())

        context = {
            'product_data': product_data,
            'user_data': user_data,
            'total_price': total_price,
        }
        return render(request, 'checkout.html', context)
    except Exception as e:
        logger.error(f'Error in checkout view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})

@login_required(login_url='login')
def ssh_console_payment(request):
    logger.info('Accessed ssh_console_payment view')
    try:
        return render(request, 'console.html')
    except Exception as e:
        logger.error(f'Error in ssh_console_payment view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})