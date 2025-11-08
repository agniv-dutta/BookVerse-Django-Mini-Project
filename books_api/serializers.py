# books_api/serializers.py
from rest_framework import serializers
from BookOutlet.models import Book  # assuming you have Book model

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author']