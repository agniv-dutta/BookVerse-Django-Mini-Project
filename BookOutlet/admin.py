from django.contrib import admin
from .models import Book, Review, UserInfo, UserProfile

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price", "copies_available")
    list_filter = ("copies_available",)
    search_fields = ("title", "author", "isbn")
    list_editable = ("price", "copies_available")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("book__title", "user__username", "comment")
    date_hierarchy = "created_at"

@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "text")
    search_fields = ("name", "email")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "birth_date")
    list_filter = ("location", "birth_date")
    search_fields = ("user__username", "bio", "favorite_genres")
    readonly_fields = ("user",)
    
    # For better display in admin
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'birth_date')
        }),
        ('Profile Details', {
            'fields': ('bio', 'location', 'favorite_genres', 'avatar')
        }),
    )