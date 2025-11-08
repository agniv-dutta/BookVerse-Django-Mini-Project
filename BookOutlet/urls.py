from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'book_outlet'

urlpatterns = [
    # Home page - KEEP ONLY ONE
    path("", views.home_view, name="home"),
    
    # Book list views
    path("books/raw/", views.book_list, name="book_list_raw"),
    path("books/", views.book_list_template, name="book_list"),
    path("books/<int:pk>/", views.book_detail, name="book_details"),
    path("cbv/books/", views.BookListView.as_view(), name="cbv_book_list"),
    path("cbv/books/<int:pk>/", views.BookDetailView.as_view(), name="cbv_book_details"),
    
    # Form URLs
    path("add-book/", views.add_book, name="add_book"),
    path("add-book-class/", views.AddBookView.as_view(), name="add_book_class"),
    path("add-user-info/", views.add_user_info, name="add_user_info"),
    path("add-user-info-class/", views.AddUserInfoView.as_view(), name="add_user_info_class"),
    path("success/", views.success_page, name="success_page"),
    
    # Admin view 
    path("admin-submissions/", views.admin_submissions, name="admin_submissions"),
    
    # React URLs
    path("react-books/", views.react_books_view, name="react_books"),
    
    # API endpoints
    path("api/books/json/", views.books_api_json, name="books_api_json"),
    path("api/stats/", views.book_stats_api, name="book_stats_api"),
    
    # Authentication URLs - USE EITHER THESE OR THE ONES BELOW, NOT BOTH
    path("register/", views.register_view, name="register"),
    path("search/", views.book_search_view, name="book_search"),
    path("profile/", views.profile_view, name="profile"),
    path("book/<int:book_id>/review/", views.add_review, name="add_review"),
    path("review/<int:review_id>/delete/", views.delete_review, name="delete_review"),
    
    
    # Use Django's built-in auth views instead of your custom ones
    path('accounts/login/', auth_views.LoginView.as_view(template_name='book_outlet/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Order URLs
    path("order/place/", views.place_order, name="place_order"),
    path("orders/", views.order_list, name="order_list"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("order/<int:order_id>/payment/", views.process_payment, name="process_payment"),

    path("logout/", auth_views.LogoutView.as_view(next_page='/book-outlet/'), name="logout"),
]