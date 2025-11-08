# BookVerse - Django Bookstore

A full-featured online bookstore built with Django, featuring book listings, user authentication, shopping cart, and order management.

## 🚀 Features

- **Book Management**: Browse, search, and view book details
- **User Authentication**: Secure registration and login system
- **Shopping Cart**: Add/remove books with quantity management
- **Order Tracking**: Complete order history and status tracking
- **User Profiles**: Personalized user profiles with order history
- **REST API**: JSON API for book data and operations
- **Responsive Design**: Bootstrap-powered responsive interface

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: SQLite (Development), PostgreSQL ready
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Authentication**: Django Auth System
- **API**: Django REST Framework

## 📦 Project Structure
BookVerse/

├── BookStore/ # Django project settings

├── BookOutlet/ # Main bookstore app

│ ├── templates/ # HTML templates

│ ├── models.py # Database models

│ ├── views.py # View logic

│ └── urls.py # URL routing

├── books_api/ # REST API app

│ ├── serializers.py # API serializers

│ └── views.py # API views

└── manage.py # Django management script


## 🚀 Installation

1. **Clone the repository**
   ```
    git clone https://github.com/agniv-dutta/BookVerse-Django-Mini-Project.git
    
   cd BookVerse-Django-Mini-Project
2. **Set up virtual environment**
   ```
    python -m venv venv
    source venv/bin/activate # Linux/Mac
    venv\Scripts\activate # Windows
3. **Install Dependencies**
   ```
    pip install -r requirements.txt
4. **Run Migrations**
   ```
    python manage.py migrate
5. **Create superuser**
   ```
    python manage.py createsuperuser
6. **Run development server**
   ```
    python manage.py runserver

## 📚 API Endpoints

- `GET /api/books/` - List all books
- `GET /api/books/<id>/` - Get book details  
- `POST /api/orders/` - Create new order
- `GET /api/users/profile/` - User profile data

## 🎯 Usage

- **Browse Books**: Visit the home page to see available books
- **User Registration**: Create an account to access full features
- **Add to Cart**: Select books and add them to your shopping cart
- **Checkout**: Complete purchase and track orders
- **Profile Management**: Update your personal information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

**Agniv Dutta**  
GitHub: [@agniv-dutta](https://github.com/agniv-dutta)

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap for UI components
