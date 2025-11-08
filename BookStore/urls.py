# BookStore/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('book-outlet/', include('BookOutlet.urls', namespace='book_outlet')),  # ← This line is crucial
    path('api/', include('books_api.urls')),  # new API endpoints

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='book_outlet/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/book-outlet/'), name='logout'),
]