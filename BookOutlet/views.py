from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg
from .models import Book, UserInfo, UserProfile, Review, Cart, CartItem, Order, OrderItem, User
from .forms import BookForm, UserInfoForm, ReviewForm
import time

# ===== AUTHENTICATION VIEWS =====
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to BookStore.')
            return redirect('book_outlet:book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'book_outlet/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', reverse('book_outlet:book_list'))
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'book_outlet/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('book_outlet:book_list')

@login_required
def profile_view(request):
    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'book_outlet/profile.html', {
        'user_reviews': user_reviews
    })

# ===== BOOK VIEWS =====
def book_list(request):
    books = Book.objects.all()
    output = ", ".join([str(book) for book in books])
    return HttpResponse(output)

def book_list_template(request):
    books = Book.objects.all().order_by('-id')
    return render(request, "book_outlet/book_list.html", {"books": books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all().order_by('-created_at')
    user_review = None
    
    if request.user.is_authenticated:
        user_review = Review.objects.filter(book=book, user=request.user).first()
    
    return render(request, "book_outlet/book_details.html", {
        "book": book,
        "reviews": reviews,
        "user_review": user_review
    })

class BookListView(View):
    def get(self, request):
        books = Book.objects.all().order_by('-id')
        return render(request, "book_outlet/book_list.html", {"books": books})

class BookDetailView(View):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        reviews = book.reviews.all().order_by('-created_at')
        user_review = None
        
        if request.user.is_authenticated:
            user_review = Review.objects.filter(book=book, user=request.user).first()
        
        return render(request, "book_outlet/book_details.html", {
            "book": book,
            "reviews": reviews,
            "user_review": user_review
        })

# ===== ADVANCED SEARCH VIEW =====
def book_search_view(request):
    books = Book.objects.all()
    
    # Get filter parameters
    search_query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_rating = request.GET.get('min_rating', '')
    sort_by = request.GET.get('sort_by', 'newest')
    
    # Apply filters
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    if genre_filter:
        books = books.filter(genre__iexact=genre_filter)
    
    if min_price:
        try:
            books = books.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            books = books.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if min_rating:
        try:
            books = books.filter(rating__gte=float(min_rating))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        books = books.order_by('price')
    elif sort_by == 'price_high':
        books = books.order_by('-price')
    elif sort_by == 'rating':
        books = books.order_by('-rating')
    elif sort_by == 'title':
        books = books.order_by('title')
    else:  # newest
        books = books.order_by('-created_at')
    
    # Get unique genres for filter dropdown
    genres = Book.objects.exclude(genre__isnull=True).exclude(genre='').values_list('genre', flat=True).distinct()
    
    context = {
        'books': books,
        'genres': genres,
        'search_query': search_query,
        'current_filters': {
            'genre': genre_filter,
            'min_price': min_price,
            'max_price': max_price,
            'min_rating': min_rating,
            'sort_by': sort_by,
        }
    }
    
    return render(request, 'book_outlet/book_search.html', context)

# ===== BOOK FORM VIEWS =====
@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            try:
                book = form.save(commit=False)
                book.created_by = request.user
                book.save()
                messages.success(request, f'Book "{form.cleaned_data["title"]}" added successfully!')
                return redirect(reverse('book_outlet:book_list'))
            except ValidationError as e:
                for field, errors in e.error_dict.items():
                    for error in errors:
                        form.add_error(field, error)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm()
    
    return render(request, 'book_outlet/add_book.html', {'form': form})

class AddBookView(LoginRequiredMixin, View):
    def get(self, request):
        form = BookForm()
        return render(request, 'book_outlet/add_book.html', {'form': form})
    
    def post(self, request):
        form = BookForm(request.POST)
        if form.is_valid():
            try:
                book = form.save(commit=False)
                book.created_by = request.user
                book.save()
                messages.success(request, f'Book "{form.cleaned_data["title"]}" added successfully!')
                return redirect(reverse('book_outlet:book_list'))
            except ValidationError as e:
                for field, errors in e.error_dict.items():
                    for error in errors:
                        form.add_error(field, error)
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'book_outlet/add_book.html', {'form': form})

# ===== REVIEW VIEWS =====
@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # Check if user already reviewed this book
    existing_review = Review.objects.filter(book=book, user=request.user).first()
    
    if request.method == 'POST':
        if existing_review:
            # Update existing review
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            # Create new review
            form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('book_outlet:book_detail', pk=book.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm(instance=existing_review)
    
    return render(request, 'book_outlet/add_review.html', {
        'form': form, 
        'book': book,
        'existing_review': existing_review
    })

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    book_id = review.book.id
    review.delete()
    
    messages.success(request, 'Review deleted successfully!')
    return redirect('book_outlet:book_detail', pk=book_id)

# ===== USER INFO FORM VIEWS =====
def add_user_info(request):
    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect(reverse('book_outlet:success_page'))
            except ValidationError as e:
                for field, errors in e.error_dict.items():
                    for error in errors:
                        form.add_error(field, error)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserInfoForm()
    
    return render(request, 'book_outlet/user_info_form.html', {'form': form})

class AddUserInfoView(View):
    def get(self, request):
        form = UserInfoForm()
        return render(request, 'book_outlet/user_info_form.html', {'form': form})
    
    def post(self, request):
        form = UserInfoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect(reverse('book_outlet:success_page'))
            except ValidationError as e:
                for field, errors in e.error_dict.items():
                    for error in errors:
                        form.add_error(field, error)
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'book_outlet/user_info_form.html', {'form': form})

# ===== UTILITY VIEWS =====
def success_page(request):
    return render(request, 'book_outlet/success.html')

def admin_submissions(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff permission required.')
        return redirect(reverse('book_outlet:book_list'))
    
    books = Book.objects.all().order_by('-id')
    user_infos = UserInfo.objects.all().order_by('-id')
    reviews = Review.objects.all().order_by('-created_at')
    
    return render(request, 'book_outlet/admin_submissions.html', {
        'books': books,
        'user_infos': user_infos,
        'reviews': reviews
    })

def react_books_view(request):
    """View that combines Django templates with React components"""
    books = Book.objects.all().order_by('-id')
    return render(request, 'book_outlet/react_books.html', {
        'books': books
    })

# ===== HOME & LANDING PAGES =====
'''def home_view(request):
    """Home page with featured books and statistics"""
    featured_books = Book.objects.filter(is_featured=True)[:6]
    recent_books = Book.objects.all().order_by('-created_at')[:6]
    top_rated_books = Book.objects.exclude(rating__isnull=True).order_by('-rating')[:6]
    
    stats = {
        'total_books': Book.objects.count(),
        'total_reviews': Review.objects.count(),
        'featured_books': featured_books.count(),
    }
    
    return render(request, 'book_outlet/home.html', {
        'featured_books': featured_books,
        'recent_books': recent_books,
        'top_rated_books': top_rated_books,
        'stats': stats
    })'''
'''def home_view(request):
    """Home page with featured books and statistics"""
    # Use existing fields from your Book model
    all_books = Book.objects.all()
    
    # Get recent books using ID (assuming newer books have higher IDs)
    recent_books = all_books.order_by('-id')[:6]
    
    # For featured books, use the first few books
    featured_books = all_books[:6]
    
    stats = {
        'total_books': all_books.count(),
        'total_reviews': Review.objects.count(),
        'featured_books': 6,  # Static count for featured section
    }
    
    return render(request, 'book_outlet/book_list.html', {
        'featured_books': featured_books,
        'recent_books': recent_books,
        'stats': stats,
        'books': all_books  # Pass 'books' for book_list.html compatibility
    })'''
def home_view(request):
    """Home page with dashboard and about us section"""
    # Get some books for featured sections
    all_books = Book.objects.all()
    recent_books = all_books.order_by('-id')[:4]  # 4 most recent books
    
    cart_items_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.items.count()
        except Cart.DoesNotExist:
            pass

    stats = {
        'total_books': all_books.count(),
        'total_reviews': Review.objects.count(),
        'total_users': User.objects.count(),
        'cart_items_count': cart_items_count,  
    }
    
    return render(request, 'book_outlet/home.html', {
        'recent_books': recent_books,
        'stats': stats
    })

# ===== API-LIKE VIEWS FOR REACT COMPONENTS =====
def books_api_json(request):
    """Simple JSON API for React components"""
    books = Book.objects.all().values('id', 'title', 'author', 'genre', 'price', 'rating')
    return JsonResponse(list(books), safe=False)

def book_stats_api(request):
    """API endpoint for book statistics"""
    stats = {
        'total_books': Book.objects.count(),
        'total_reviews': Review.objects.count(),
        'average_rating': Book.objects.exclude(rating__isnull=True).aggregate(Avg('rating'))['rating__avg'] or 0,
        'featured_books': Book.objects.filter(is_featured=True).count(),
    }
    
    return JsonResponse(stats)

@login_required
def cart(request):
    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    total_price = sum(item.get_total_price() for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    return render(request, 'book_outlet/cart.html', context)

@login_required
def add_to_cart(request, book_id):
    if request.method == 'POST':
        try:
            book = Book.objects.get(id=book_id)
            quantity = int(request.POST.get('quantity', 1))
            
            # Get or create user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Check if book is already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                book=book,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # If item already exists, update quantity
                cart_item.quantity += quantity
                cart_item.save()
            
            messages.success(request, f"Added {book.title} to cart!")
            
        except Book.DoesNotExist:
            messages.error(request, "Book not found.")
        except ValueError:
            messages.error(request, "Invalid quantity.")
    
    return redirect('book_outlet:book_list')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Quantity increased!')
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, 'Quantity decreased!')
        elif action == 'remove':
            book_title = cart_item.book.title
            cart_item.delete()
            messages.success(request, f'Removed {book_title} from cart!')
    
    return redirect('book_outlet:view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.success(request, f'Removed {book_title} from cart!')
    return redirect('book_outlet:view_cart')

@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        total_price = cart.get_total_price()
        total_quantity = cart.get_total_quantity()  # Add this line
        
        print(f"DEBUG: Cart found with {cart_items.count()} items")  # Debug
        print(f"DEBUG: Total quantity: {total_quantity}")  # Debug
        
    except Cart.DoesNotExist:
        # If no cart exists, create an empty one
        cart = None
        cart_items = []
        total_price = 0
        total_quantity = 0  # Add this line
        print("DEBUG: No cart found for user")  # Debug
    
    return render(request, 'book_outlet/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity  
    })

@login_required
def place_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('book_outlet:view_cart')
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '')
        
        if not shipping_address:
            messages.error(request, 'Please provide a shipping address!')
            return redirect('book_outlet:checkout')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.get_total_price(),
            shipping_address=shipping_address
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=cart_item.book,
                quantity=cart_item.quantity,
                price=cart_item.book.price if cart_item.book.price else 0
            )
        
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, f'Order #{order.order_number} placed successfully!')
        return redirect('book_outlet:order_detail', order_id=order.id)
    
    # GET request - show checkout page
    return render(request, 'book_outlet/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_total_price()
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'book_outlet/order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'book_outlet/order_detail.html', {
        'order': order
    })

@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status:
        messages.info(request, 'Payment already processed!')
        return redirect('book_outlet:order_detail', order_id=order.id)
    
    # Simulate payment processing
    order.payment_status = True
    order.status = 'confirmed'
    order.save()
    
    messages.success(request, f'Payment successful for Order #{order.order_number}!')
    return redirect('book_outlet:order_detail', order_id=order.id)

def profile_view(request):
    """User profile page"""
    if not request.user.is_authenticated:
        return redirect('book_outlet:login')
    
    # If you have UserProfile model
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    
    return render(request, 'book_outlet/profile.html', {
        'profile': profile
    })

def checkout(request):
    # Get the user's cart and then the cart items
    try:
        # Get the user's cart
        cart = Cart.objects.get(user=request.user)
        # Get cart items through the cart relationship
        cart_items = CartItem.objects.filter(cart=cart)
        
        total_price = sum(item.get_total_price() for item in cart_items)
        
        if request.method == 'POST':
            # Handle the checkout process
            shipping_address = request.POST.get('shipping_address', '')
            
            if not shipping_address.strip():
                messages.error(request, "Please provide a shipping address.")
                return render(request, 'book_outlet/checkout.html', {
                    'cart_items': cart_items,
                    'total_price': total_price
                })
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=total_price,
                shipping_address=shipping_address,
                status='pending'
            )
            
            # Add cart items to order
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    quantity=item.quantity,
                    price=item.book.price
                )
            
            # Clear the cart after order creation
            cart_items.delete()
            
            messages.success(request, f"Order #{order.order_number} created successfully!")
            return redirect('book_outlet:order_detail', order_id=order.id)
        
    except Cart.DoesNotExist:
        # If user doesn't have a cart yet
        cart_items = CartItem.objects.none()
        total_price = 0
        messages.error(request, "Your cart is empty.")
        return redirect('book_outlet:cart')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'book_outlet/checkout.html', context)