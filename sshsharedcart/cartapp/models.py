from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
# Supermarket model
class Supermarket(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=100)
    
    calories = models.IntegerField(default=0)
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    carbohydrates = models.FloatField()
    fat = models.FloatField()
    
    is_healthy = models.BooleanField(default=False)
    health_score = models.IntegerField(default=50)
    
    image = models.CharField(max_length=255, default="images/products/AlmondMilk.jpeg")

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = f"images/products/{''.join(self.name.split())}.jpeg"
        super().save(*args, **kwargs)
    
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE, related_name='grocery_items')
    
    def __str__(self):
        return self.name
    
# Cart model
class Cart(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='shared_carts')
    
    def __str__(self):
        return f"Shared Cart {self.id}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Made nullable

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity