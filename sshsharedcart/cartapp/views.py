from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupFormStep1, SignupFormStep2
from .models import Product, Cart, CartItem, Supermarket
from collections import defaultdict

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignupFormStep1(request.POST)
        if form.is_valid():
            request.session['signup_email'] = form.cleaned_data['email']
            return redirect('signup_step2')
    else:
        form = SignupFormStep1()
    return render(request, 'registration/signup.html', {'form': form})

def signup_step2(request):
    if 'signup_email' not in request.session:
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

            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('supermarkets')
    else:
        form = SignupFormStep2()
    return render(request, 'registration/signup_step2.html', {'form': form})

@login_required(login_url='login')
def supermarkets(request):
    supermarkets = Supermarket.objects.all()
    selected_supermarket_id = request.GET.get('supermarket')
    search_query = request.GET.get('search', '')

    products = Product.objects.all()
    if selected_supermarket_id:
        products = products.filter(supermarket__id=selected_supermarket_id)
    if search_query:
        products = products.filter(name__icontains=search_query)

    context = {
        'supermarkets': supermarkets,
        'products': products,
        'selected_supermarket_id': selected_supermarket_id,
        'search_query': search_query,
    }
    return render(request, 'supermarkets.html', context)

@login_required(login_url='login')
def shared_cart(request):
    cart, created = Cart.objects.get_or_create(name='Shared Cart')
    cart.users.add(request.user)
    total_price = sum(item.total_price for item in cart.items.all())
    context = {'cart': cart, 'total_price': total_price}
    return render(request, 'shared_cart.html', context)

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(name='Shared Cart')
    cart.users.add(request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        added_by=request.user,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'Added {product.name} to cart.')
    
    next_url = request.POST.get('next', 'supermarkets')
    return redirect(next_url)

@login_required(login_url='login')
def update_quantity(request, item_id):
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

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('shared_cart')