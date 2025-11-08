from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re
import time

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100, default="Unknown Author")
    
    # NEW FIELDS FOR PHASE 1
    genre = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Price in INR")
    rating = models.FloatField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    copies_available = models.PositiveIntegerField(
        default=1,
        help_text="Number of copies in inventory"
    )
    isbn = models.CharField(
        max_length=13, 
        blank=True, 
        null=True,
        help_text="International Standard Book Number"
    )

    cover_image = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Book cover image filename"
    )


    def clean(self):
        errors = {}
        
        # Title validation
        if not self.title or not self.title.strip():
            errors['title'] = 'Title cannot be empty.'
        elif not self.title[0].isupper():
            errors['title'] = 'Title must start with a capital letter.'
        
        # Author validation
        if not self.author or not self.author.strip():
            errors['author'] = 'Author cannot be empty.'
        elif len(self.author.split()) < 2:
            errors['author'] = 'Author should be in "First Last" format.'
        elif not all(word[0].isupper() for word in self.author.split() if word):
            errors['author'] = 'Each word in author name must start with a capital letter.'
        elif not re.match(r'^[A-Za-z\s\.]+$', self.author):  # Updated to allow periods for initials
            errors['author'] = 'Author name can only contain letters, spaces, and periods.'
        
        # Price validation (if provided)
        if self.price is not None and self.price < 0:
            errors['price'] = 'Price cannot be negative.'
        
        # Rating validation (if provided)
        if self.rating is not None and (self.rating < 0 or self.rating > 5):
            errors['rating'] = 'Rating must be between 0 and 5.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_cover_url(self):
        if self.cover_image:
            return f'/static/book_outlet/images/book_covers/{self.cover_image}'
        return '/static/book_outlet/images/book_covers/default_cover.jpg'
    
    def get_average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return None
    
    def get_review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    def is_in_stock(self):
        return self.copies_available > 0


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    favorite_genres = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.user.username
    
    def clean(self):
        errors = {}
        
        # Bio validation
        if self.bio and len(self.bio.strip()) > 500:
            errors['bio'] = 'Bio cannot exceed 500 characters.'
        
        # Favorite genres validation
        if self.favorite_genres and len(self.favorite_genres) > 200:
            errors['favorite_genres'] = 'Favorite genres cannot exceed 200 characters.'
        
        if errors:
            raise ValidationError(errors)


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['book', 'user']  # One review per user per book
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.rating} stars"
    
    def clean(self):
        errors = {}
        
        # Rating validation
        if self.rating not in [1, 2, 3, 4, 5]:
            errors['rating'] = 'Rating must be between 1 and 5.'
        
        # Comment validation
        if not self.comment or not self.comment.strip():
            errors['comment'] = 'Comment cannot be empty.'
        elif len(self.comment.strip()) > 1000:
            errors['comment'] = 'Comment cannot exceed 1000 characters.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update book's average rating when review is saved
        self.update_book_rating()
    
    def update_book_rating(self):
        """Update the book's average rating"""
        book = self.book
        reviews = book.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            book.rating = round(avg_rating, 1)
        else:
            book.rating = None
        book.save()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart ({self.user.username})"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
    
    def get_total_price(self):
        return self.book.price * self.quantity if self.book.price else 0

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField(blank=True)
    payment_status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{self.user.id}{int(time.time())}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
    
    def get_total_price(self):
        return self.price * self.quantity
    
class UserInfo(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    verify_email = models.EmailField()
    text = models.TextField()
    
    def clean(self):
        errors = {}
        
        # Name validation
        if not self.name or not self.name.strip():
            errors['name'] = 'Name cannot be empty.'
        
        # Email validation
        if self.email != self.verify_email:
            errors['verify_email'] = 'Emails do not match.'
        
        # Text validation
        if not self.text or not self.text.strip():
            errors['text'] = 'Message cannot be empty.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


# Signal to create UserProfile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()