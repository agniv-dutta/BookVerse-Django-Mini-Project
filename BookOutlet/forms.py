from django import forms
from .models import Book, UserInfo, Review

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'copies_available', 'isbn']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title',
                'autofocus': True
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter author name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'copies_available': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1',
                'min': '0'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional ISBN'
            }),
        }
        error_messages = {
            'title': {
                'required': 'Please enter a book title.',
                'max_length': 'Title must be less than 100 characters.'
            },
            'author': {
                'required': 'Please enter an author name.',
                'max_length': 'Author name must be less than 100 characters.'
            },
        }

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['name', 'email', 'verify_email', 'text']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'verify_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm your email'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your message',
                'rows': 4
            }),
        }
        error_messages = {
            'name': {'required': 'Please enter your name.'},
            'email': {'required': 'Please enter your email.'},
            'verify_email': {'required': 'Please confirm your email.'},
            'text': {'required': 'Please enter a message.'},
        }
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        verify_email = cleaned_data.get('verify_email')
        
        if email and verify_email and email != verify_email:
            raise forms.ValidationError({
                'verify_email': 'Email addresses must match.'
            })
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['book', 'user', 'rating', 'comment']
        widgets = {
            'book': forms.Select(attrs={
                'class': 'form-control'
            }),
            'user': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control',
                'choices': 'RATING_CHOICES'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your review comment',
                'rows': 4
            }),
        }
        error_messages = {
            'rating': {'required': 'Please select a rating.'},
            'comment': {'required': 'Please enter a review comment.'},
        }