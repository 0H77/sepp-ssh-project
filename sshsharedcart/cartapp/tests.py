from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from .models import Cart, CartItem, Product, Supermarket, Profile, User
import logging

# Create your tests here.
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

USERNAME = 'testuser'
PASSWORD = 'testpass'

class CheckoutViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        
        cls.supermarket = Supermarket.objects.create(name='Test Supermarket', location='Test Location')
        
        cls.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.99'),
            category='Test Category',
            calories=100, 
            protein=Decimal('10.5'), 
            carbohydrates=Decimal('20.5'), 
            fat=Decimal('5.5'),
            is_healthy=True, 
            health_score=80,
            image='images/products/TestProduct.jpeg',
            supermarket=cls.supermarket
        )
        
        cls.product2 = Product.objects.create(
            name='Second Test Product',
            price=Decimal('5.50'),
            category='Test Category',
            calories=50, 
            protein=Decimal('5.0'), 
            carbohydrates=Decimal('10.0'), 
            fat=Decimal('2.5'),
            is_healthy=True, 
            health_score=70,
            image='images/products/SecondTestProduct.jpeg',
            supermarket=cls.supermarket
        )
        
        cls.cart = Cart.objects.create(name='Shared Cart')
        cls.cart.users.add(cls.user)
    
    def setUp(self):
        self.client.login(username=USERNAME, password=PASSWORD)
    
    def test_checkout_page_loads(self):
        logging.info('Testing if checkout page loads correctly')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout.html')
    
    def test_checkout_page_redirects_if_not_logged_in(self):
        logging.info('Testing checkout page redirects when not logged in')
        self.client.logout()
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, '/login/?next=/checkout/')
    
    def test_checkout_page_shows_total(self):
        logging.info('Testing if checkout page shows total')
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            added_by=self.user
        )
        response = self.client.get(reverse('checkout'))
        self.assertContains(response, 'Total')
    
    def test_checkout_page_shows_checkout_button(self):
        logging.info('Testing if checkout page shows checkout button')
        response = self.client.get(reverse('checkout'))
        self.assertContains(response, 'Checkout')
    
    def test_checkout_page_shows_empty_cart_message(self):
        logging.info('Testing if checkout page shows empty cart message')
        self.cart.items.all().delete()
        response = self.client.get(reverse('checkout'))
        self.assertContains(response, 'Your cart is empty')
    
    def test_checkout_page_shows_cart_items(self):
        logging.info('Testing if checkout page shows cart items')
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
            added_by=self.user
        )
        response = self.client.get(reverse('checkout'))
        self.assertContains(response, cart_item.product.name)
        self.assertContains(response, cart_item.quantity)
    
    def test_checkout_page_shows_total_price(self):
        logging.info('Testing if checkout page shows total price')
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            added_by=self.user
        )
        response = self.client.get(reverse('checkout'))
        total_price = cart_item.product.price * cart_item.quantity
        formatted_total_price = f"{total_price:.2f}"
        self.assertContains(response, formatted_total_price)
    
    def test_checkout_page_shows_total_price_for_multiple_items(self):
        logging.info('Testing if checkout page shows total price for multiple items')
        cart_item1 = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            added_by=self.user
        )
        cart_item2 = CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=3,
            added_by=self.user
        )
        response = self.client.get(reverse('checkout'))
        
        total_price1 = cart_item1.product.price * cart_item1.quantity
        total_price2 = cart_item2.product.price * cart_item2.quantity
        total_price = total_price1 + total_price2
        formatted_total_price = f"{total_price:.2f}"
        
        self.assertContains(response, formatted_total_price)

class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.profile, _ = Profile.objects.get_or_create(user=cls.user, defaults={'address': '123 Test St'})
    
    def test_profile_str_method(self):
        logging.info('Testing profile __str__ method')
        self.assertEqual(str(self.profile), self.user.username)

class SupermarketModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.supermarket = Supermarket.objects.create(name='Test Supermarket', location='Test Location')
    
    def test_supermarket_str_method(self):
        logging.info('Testing Supermarket __str__ method')
        self.assertEqual(str(self.supermarket), 'Test Supermarket')

class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.supermarket = Supermarket.objects.create(name='Test Supermarket', location='Test Location')
        cls.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.99'),
            category='Test Category',
            calories=100, 
            protein=Decimal('10.5'), 
            carbohydrates=Decimal('20.5'), 
            fat=Decimal('5.5'),
            is_healthy=True, 
            health_score=80,
            image='images/products/TestProduct.jpeg',
            supermarket=cls.supermarket
        )
    
    def test_product_str_method(self):
        logging.info('Testing Product __str__ method')
        self.assertEqual(str(self.product), 'Test Product')

class CartModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cart = Cart.objects.create(name='Shared Cart')
    
    def test_cart_str_method(self):
        logging.info('Testing Cart __str__ method')
        self.assertEqual(str(self.cart), f"Shared Cart {self.cart.id}")

class CartItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.supermarket = Supermarket.objects.create(name='Test Supermarket', location='Test Location')
        cls.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.99'),
            category='Test Category',
            calories=100, 
            protein=Decimal('10.5'), 
            carbohydrates=Decimal('20.5'), 
            fat=Decimal('5.5'),
            is_healthy=True, 
            health_score=80,
            image='images/products/TestProduct.jpeg',
            supermarket=cls.supermarket
        )
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.cart = Cart.objects.create(name='Shared Cart')
        cls.cart.users.add(cls.user)
        cls.cart_item = CartItem.objects.create(
            cart=cls.cart,
            product=cls.product,
            quantity=2,
            added_by=cls.user
        )
    
    def test_cart_item_str_method(self):
        logging.info('Testing CartItem __str__ method')
        self.assertEqual(str(self.cart_item), f"{self.cart_item.quantity} x {self.cart_item.product.name}")
    
    def test_cart_item_total_price_property(self):
        logging.info('Testing CartItem total_price property')
        self.assertEqual(self.cart_item.total_price, Decimal('21.98'))
    
    def test_cart_item_total_price_property_multiple_items(self):
        logging.info('Testing CartItem total_price property with multiple items')
        product2 = Product.objects.create(
            name='Second Test Product',
            price=Decimal('5.50'),
            category='Test Category',
            calories=50,
            protein=Decimal('5.0'),
            carbohydrates=Decimal('10.0'),
            fat=Decimal('2.5'),
            is_healthy=True,
            health_score=70,
            image='images/products/SecondTestProduct.jpeg',
            supermarket=self.supermarket
        )
        cart_item2 = CartItem.objects.create(
            cart=self.cart,
            product=product2,
            quantity=3,
            added_by=self.user
        )
        self.assertEqual(self.cart_item.total_price, Decimal('21.98'))
        self.assertEqual(cart_item2.total_price, Decimal('16.50'))

class SharedCartViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.cart = Cart.objects.create(name='Shared Cart')
        cls.cart.users.add(cls.user)
        cls.supermarket = Supermarket.objects.create(name='Shared Market', location='Shared Location')
        cls.product = Product.objects.create(
            name='Shared Cart Product',
            price=Decimal('15.00'),
            category='Shared Category',
            calories=200,
            protein=Decimal('20.0'),
            carbohydrates=Decimal('30.0'),
            fat=Decimal('10.0'),
            is_healthy=True,
            health_score=85,
            image='images/products/SharedCartProduct.jpeg',
            supermarket=cls.supermarket
        )
        cls.cart_item = CartItem.objects.create(
            cart=cls.cart,
            product=cls.product,
            quantity=1,
            added_by=cls.user
        )
    
    def setUp(self):
        self.client.login(username=USERNAME, password=PASSWORD)
    
    def test_shared_cart_page_loads(self):
        logging.info('Testing if shared cart page loads correctly')
        response = self.client.get(reverse('shared_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared_cart.html')
    
    def test_shared_cart_page_shows_cart(self):
        logging.info('Testing if shared cart page shows cart')
        response = self.client.get(reverse('shared_cart'))
        self.assertContains(response, 'Shared Cart')
    
    def test_shared_cart_page_shows_total_price(self):
        logging.info('Testing if shared cart page shows total price')
        response = self.client.get(reverse('shared_cart'))
        total_price = self.cart_item.product.price * self.cart_item.quantity
        formatted_total_price = f"{total_price:.2f}"
        self.assertContains(response, formatted_total_price)
    
    def test_shared_cart_page_shows_empty_cart_message(self):
        logging.info('Testing if shared cart page shows empty cart message')
        self.cart.items.all().delete()
        response = self.client.get(reverse('shared_cart'))
        self.assertContains(response, 'Your cart is empty')

class AddToCartViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.supermarket = Supermarket.objects.create(name='Add Market', location='Add Location')
        cls.product = Product.objects.create(
            name='Add Product',
            price=Decimal('5.99'),
            category='Add Category',
            calories=60,
            protein=Decimal('6.0'),
            carbohydrates=Decimal('12.0'),
            fat=Decimal('3.0'),
            is_healthy=True,
            health_score=75,
            image='images/products/AddProduct.jpeg',
            supermarket=cls.supermarket
        )
        cls.cart = Cart.objects.create(name='Add Cart')
        cls.cart.users.add(cls.user)
    
    def setUp(self):
        self.client.login(username=USERNAME, password=PASSWORD)
    
    def test_add_to_cart_view_redirects_to_supermarkets(self):
        logging.info('Testing add to cart view redirects to supermarkets')
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 1})
        self.assertRedirects(response, reverse('supermarkets'))

class UpdateQuantityViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.supermarket = Supermarket.objects.create(name='Update Market', location='Update Location')
        cls.product = Product.objects.create(
            name='Update Product',
            price=Decimal('7.99'),
            category='Update Category',
            calories=80,
            protein=Decimal('8.0'),
            carbohydrates=Decimal('16.0'),
            fat=Decimal('4.0'),
            is_healthy=True,
            health_score=78,
            image='images/products/UpdateProduct.jpeg',
            supermarket=cls.supermarket
        )
        cls.cart = Cart.objects.create(name='Update Cart')
        cls.cart.users.add(cls.user)
        cls.cart_item = CartItem.objects.create(cart=cls.cart, product=cls.product, quantity=1, added_by=cls.user)
    
    def setUp(self):
        self.client.login(username=USERNAME, password=PASSWORD)
    
    def test_update_quantity_view_redirects_if_not_logged_in(self):
        logging.info('Testing update quantity view redirects when not logged in')
        self.client.logout()
        response = self.client.post(reverse('update_quantity', args=[self.cart_item.id]), {'quantity': 5})
        expected_url = f'/login/?next=/cart/update/{self.cart_item.id}/'
        self.assertRedirects(response, expected_url)
    
    def test_update_quantity_view_redirects_to_shared_cart(self):
        logging.info('Testing update quantity view redirects to shared cart')
        response = self.client.post(reverse('update_quantity', args=[self.cart_item.id]), {
            'quantity': 5
        })
        self.assertRedirects(response, reverse('shared_cart'))
    
    def test_update_quantity_view_updates_quantity(self):
        logging.info('Testing update quantity view updates item quantity')
        response = self.client.post(reverse('update_quantity', args=[self.cart_item.id]), {
            'quantity': 4
        })
        self.assertEqual(response.status_code, 302)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 4)
    
    def test_update_quantity_view_does_not_update_other_users_items(self):
        logging.info('Testing update quantity view does not update other users\' items')
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        other_cart = Cart.objects.create(name='Other Cart')
        other_cart.users.add(other_user)
        other_cart_item = CartItem.objects.create(cart=other_cart, product=self.product, quantity=2, added_by=other_user)
        
        response = self.client.post(reverse('update_quantity', args=[other_cart_item.id]), {
            'quantity': 5
        })
        self.assertEqual(response.status_code, 302)

class SupermarketsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.supermarket1 = Supermarket.objects.create(name='Supermarket 1', location='Location 1')
        cls.supermarket2 = Supermarket.objects.create(name='Supermarket 2', location='Location 2')
        cls.product1 = Product.objects.create(
            name='Product 1',
            price=Decimal('12.99'),
            category='Category 1',
            calories=150,
            protein=Decimal('15.0'),
            carbohydrates=Decimal('25.0'),
            fat=Decimal('6.0'),
            is_healthy=True,
            health_score=85,
            image='images/products/Product1.jpeg',
            supermarket=cls.supermarket1
        )
        cls.product2 = Product.objects.create(
            name='Product 2',
            price=Decimal('8.50'),
            category='Category 2',
            calories=80,
            protein=Decimal('8.0'),
            carbohydrates=Decimal('16.0'),
            fat=Decimal('3.0'),
            is_healthy=True,
            health_score=75,
            image='images/products/Product2.jpeg',
            supermarket=cls.supermarket2
        )
    
    def setUp(self):
        self.client.login(username=USERNAME, password=PASSWORD)
    
    def test_supermarkets_page_loads(self):
        logging.info('Testing if supermarkets page loads correctly')
        response = self.client.get(reverse('supermarkets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'supermarkets.html')
    
    def test_supermarkets_page_redirects_if_not_logged_in(self):
        logging.info('Testing supermarkets page redirects when not logged in')
        self.client.logout()
        response = self.client.get(reverse('supermarkets'))
        self.assertRedirects(response, '/login/?next=/supermarkets/')
    
    def test_supermarkets_page_shows_supermarkets(self):
        logging.info('Testing if supermarkets page shows supermarkets')
        response = self.client.get(reverse('supermarkets'))
        self.assertContains(response, 'Supermarket 1')
        self.assertContains(response, 'Supermarket 2')
    
    def test_supermarkets_page_shows_products(self):
        logging.info('Testing if supermarkets page shows products')
        response = self.client.get(reverse('supermarkets'))
        self.assertContains(response, 'Product 1')
        self.assertContains(response, 'Product 2')
    
    def test_supermarkets_page_filters_by_search_query(self):
        logging.info('Testing supermarkets page filtering by search query')
        response = self.client.get(reverse('supermarkets'), {'search': 'Product 1'})
        self.assertContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 2')
    
    def test_supermarkets_page_shows_search_query(self):
        logging.info('Testing supermarkets page shows search query')
        response = self.client.get(reverse('supermarkets'), {'search': 'Product 1'})
        self.assertContains(response, 'Product 1')
    
    def test_supermarkets_page_shows_image(self):
        logging.info('Testing supermarkets page shows product images')
        response = self.client.get(reverse('supermarkets'))
        self.assertContains(response, 'images/products/Product1.jpeg')
        self.assertContains(response, 'images/products/Product2.jpeg')
