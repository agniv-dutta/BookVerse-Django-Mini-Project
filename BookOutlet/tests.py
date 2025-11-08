from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Book, UserInfo
from .forms import BookForm, UserInfoForm

# Model Tests
class BookModelTest(TestCase):
    def setUpTestData(cls):
        # Run once for entire TestCase
        cls.book = Book.objects.create(
            title="The Great Gatsby",
            author="F Scott Fitzgerald"
        )
    
    def test_book_creation(self):
        """Test Book object creation and field values"""
        book = Book.objects.get(id=1)
        self.assertEqual(book.title, "The Great Gatsby")
        self.assertEqual(book.author, "F Scott Fitzgerald")
    
    def test_string_representation(self):
        """Test __str__ method returns book title"""
        book = Book.objects.get(id=1)
        self.assertEqual(str(book), "The Great Gatsby")
    
    def test_title_validation(self):
        """Test title validation rules"""
        # Test empty title
        book = Book(title="", author="Test Author")
        with self.assertRaises(ValidationError):
            book.full_clean()
        
        # Test title without capital letter
        book = Book(title="test book", author="Test Author")
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_author_validation(self):
        """Test author validation rules"""
        # Test single word author
        book = Book(title="Test Book", author="Author")
        with self.assertRaises(ValidationError):
            book.full_clean()
        
        # Test author without capital letters
        book = Book(title="Test Book", author="test author")
        with self.assertRaises(ValidationError):
            book.full_clean()
        
        # Test author with special characters
        book = Book(title="Test Book", author="Author123")
        with self.assertRaises(ValidationError):
            book.full_clean()

class UserInfoModelTest(TestCase):
    def setUp(self):
        # Run before each test
        self.user_info = UserInfo.objects.create(
            name="John Doe",
            email="john@example.com",
            verify_email="john@example.com",
            text="Test message"
        )
    
    def test_user_info_creation(self):
        """Test UserInfo object creation"""
        user = UserInfo.objects.get(id=1)
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.email, "john@example.com")
        self.assertEqual(user.text, "Test message")
    
    def test_string_representation(self):
        """Test __str__ method returns user name"""
        user = UserInfo.objects.get(id=1)
        self.assertEqual(str(user), "John Doe")
    
    def test_email_matching_validation(self):
        """Test email matching validation"""
        user = UserInfo(
            name="Test User",
            email="test@example.com",
            verify_email="different@example.com",
            text="Test"
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

# Form Tests
class BookFormTest(TestCase):
    def test_valid_form(self):
        """Test BookForm with valid data"""
        form_data = {
            'title': 'Test Book Title',
            'author': 'Test Author Name'
        }
        form = BookForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        """Test BookForm with invalid data"""
        # Test empty title
        form_data = {
            'title': '',
            'author': 'Test Author'
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Test invalid author format
        form_data = {
            'title': 'Test Book',
            'author': 'author'  # Single word, lowercase
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())

class UserInfoFormTest(TestCase):
    def test_valid_form(self):
        """Test UserInfoForm with valid data"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'verify_email': 'john@example.com',
            'text': 'This is a test message'
        }
        form = UserInfoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_email_mismatch(self):
        """Test UserInfoForm with email mismatch"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'verify_email': 'different@example.com',
            'text': 'Test message'
        }
        form = UserInfoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('verify_email', form.errors)

# View Tests
class BookListViewTest(TestCase):
    def setUp(self):
        # Create test books
        Book.objects.create(title="Book 1", author="Author One")
        Book.objects.create(title="Book 2", author="Author Two")
        self.url = reverse('book_outlet:book_list')
    
    def test_view_url_exists(self):
        """Test that book list URL exists"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        """Test that correct template is used"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'book_outlet/book_list.html')
    
    def test_view_displays_books(self):
        """Test that books are displayed in the view"""
        response = self.client.get(self.url)
        self.assertContains(response, "Book 1")
        self.assertContains(response, "Book 2")
        self.assertContains(response, "Author One")
    
    def test_view_with_no_books(self):
        """Test view when no books exist"""
        Book.objects.all().delete()  # Remove all books
        response = self.client.get(self.url)
        self.assertContains(response, "No books available")
        self.assertContains(response, "Add the first book")

class AddBookViewTest(TestCase):
    def setUp(self):
        self.url = reverse('book_outlet:add_book')
    
    def test_get_request(self):
        """Test GET request to add book form"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_outlet/add_book.html')
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="author"')
    
    def test_post_valid_data(self):
        """Test POST request with valid form data"""
        form_data = {
            'title': 'New Test Book',
            'author': 'Test Author Name'
        }
        response = self.client.post(self.url, form_data, follow=True)
        
        # Check redirect
        self.assertRedirects(response, reverse('book_outlet:book_list'))
        
        # Check book was created
        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.first()
        self.assertEqual(book.title, 'New Test Book')
        
        # Check success message
        self.assertContains(response, 'Book "New Test Book" added successfully!')
    
    def test_post_invalid_data(self):
        """Test POST request with invalid form data"""
        form_data = {
            'title': '',  # Empty title
            'author': 'Test Author'
        }
        response = self.client.post(self.url, form_data)
        
        # Should not redirect (form should be re-rendered)
        self.assertEqual(response.status_code, 200)
        
        # Book should not be created
        self.assertEqual(Book.objects.count(), 0)
        
        # Error message should be in form
        self.assertFormError(response, 'form', 'title', 'This field is required.')

class BookDetailViewTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book Detail",
            author="Test Author Detail"
        )
        self.url = reverse('book_outlet:book_details', args=[self.book.pk])
    
    def test_view_url_exists(self):
        """Test that book detail URL exists"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_view_displays_book_details(self):
        """Test that book details are displayed"""
        response = self.client.get(self.url)
        self.assertContains(response, "Test Book Detail")
        self.assertContains(response, "Test Author Detail")
        self.assertContains(response, str(self.book.pk))
    
    def test_view_404_for_invalid_book(self):
        """Test 404 for non-existent book"""
        invalid_url = reverse('book_outlet:book_details', args=[999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

class UserInfoFormViewTest(TestCase):
    def setUp(self):
        self.url = reverse('book_outlet:add_user_info')
    
    def test_get_request(self):
        """Test GET request to user info form"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_outlet/user_info_form.html')
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="email"')
    
    def test_post_valid_data(self):
        """Test POST request with valid user info"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'verify_email': 'test@example.com',
            'text': 'This is a test message'
        }
        response = self.client.post(self.url, form_data, follow=True)
        
        # Check redirect to success page
        self.assertRedirects(response, reverse('book_outlet:success_page'))
        
        # Check UserInfo was created
        self.assertEqual(UserInfo.objects.count(), 1)
        user_info = UserInfo.objects.first()
        self.assertEqual(user_info.name, 'Test User')
        
        # Check success message
        self.assertContains(response, 'Thank you for your message!')
    
    def test_post_email_mismatch(self):
        """Test POST request with email mismatch"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'verify_email': 'different@example.com',
            'text': 'Test message'
        }
        response = self.client.post(self.url, form_data)
        
        # Should not redirect
        self.assertEqual(response.status_code, 200)
        
        # UserInfo should not be created
        self.assertEqual(UserInfo.objects.count(), 0)
        
        # Error message should be present
        self.assertContains(response, 'Email addresses must match.')

class SuccessPageViewTest(TestCase):
    def test_success_page(self):
        """Test success page loads correctly"""
        url = reverse('book_outlet:success_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_outlet/success.html')
        self.assertContains(response, 'Success!')
        self.assertContains(response, 'Thank you for your submission.')