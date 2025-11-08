// BookOutlet - Main JavaScript File
console.log("BookOutlet JavaScript loaded successfully!");

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
    // Initialize all functionality
    initializeBookInteractions();
    initializeSearchFunctionality();
    initializeFormHandling();
    initializeMessageHandling();
    initializeBookCounter();
});

// Book item click interactions
function initializeBookInteractions() {
    const bookItems = document.querySelectorAll('.book-item');
    
    bookItems.forEach(function(item) {
        // Add click event to navigate to book details
        item.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            if (bookId) {
                console.log('Navigating to book ID:', bookId);
                window.location.href = '/book-outlet/books/' + bookId + '/';
            }
        });
        
        // Add hover effects
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px)';
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    console.log('Initialized book interactions for ' + bookItems.length + ' books');
}

// Search functionality for books
function initializeSearchFunctionality() {
    const searchInput = document.getElementById('book-search');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            const bookItems = document.querySelectorAll('.book-item');
            let visibleCount = 0;
            
            bookItems.forEach(function(item) {
                const bookTitle = item.querySelector('h5') ? item.querySelector('h5').textContent.toLowerCase() : '';
                const bookAuthor = item.querySelector('p') ? item.querySelector('p').textContent.toLowerCase() : '';
                const bookText = bookTitle + ' ' + bookAuthor;
                
                if (bookText.includes(searchTerm) || searchTerm === '') {
                    item.style.display = 'block';
                    visibleCount++;
                    
                    // Highlight matching text
                    if (searchTerm && bookTitle.includes(searchTerm)) {
                        item.style.borderLeftColor = '#28a745';
                        item.style.background = '#f0fff4';
                    } else {
                        item.style.borderLeftColor = '#007bff';
                        item.style.background = '#f8f9fa';
                    }
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Update search results counter
            updateSearchResultsCounter(visibleCount, bookItems.length);
        });
        
        // Add clear search button functionality
        const clearSearch = document.getElementById('clear-search');
        if (clearSearch) {
            clearSearch.addEventListener('click', function() {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            });
        }
        
        console.log('Search functionality initialized');
    }
}

// Update search results counter
function updateSearchResultsCounter(visible, total) {
    let counterElement = document.getElementById('search-results-counter');
    
    if (!counterElement) {
        counterElement = document.createElement('div');
        counterElement.id = 'search-results-counter';
        counterElement.className = 'search-counter';
        counterElement.style.margin = '10px 0';
        counterElement.style.fontSize = '14px';
        counterElement.style.color = '#6c757d';
        
        const searchContainer = document.querySelector('.row.mb-4');
        if (searchContainer) {
            searchContainer.appendChild(counterElement);
        }
    }
    
    if (visible === total) {
        counterElement.textContent = 'Showing all ' + total + ' books';
    } else {
        counterElement.textContent = 'Showing ' + visible + ' of ' + total + ' books';
    }
}

// Form handling and validation
function initializeFormHandling() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('input[type="submit"], button[type="submit"]');
            
            if (submitBtn) {
                // Disable button and show loading state
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.7';
                submitBtn.style.cursor = 'not-allowed';
                
                const originalText = submitBtn.value || submitBtn.textContent;
                submitBtn.value = 'Processing...';
                submitBtn.textContent = 'Processing...';
                
                // Re-enable button after 5 seconds (in case of error)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    submitBtn.style.cursor = 'pointer';
                    submitBtn.value = originalText;
                    submitBtn.textContent = originalText;
                }, 5000);
            }
        });
    });
    
    // Real-time form validation
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        field.addEventListener('blur', function() {
            validateEmailField(this);
        });
    });
    
    console.log('Form handling initialized for ' + forms.length + ' forms');
}

// Email validation helper
function validateEmailField(field) {
    const email = field.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        field.style.borderColor = '#dc3545';
        field.style.background = '#fff5f5';
    } else {
        field.style.borderColor = '#28a745';
        field.style.background = '#f8fff9';
    }
}

// Auto-hide success/error messages
function initializeMessageHandling() {
    const messages = document.querySelectorAll('.alert');
    
    messages.forEach(function(message) {
        // Add close button functionality
        const closeBtn = message.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                message.style.transition = 'all 0.5s ease';
                message.style.opacity = '0';
                message.style.height = '0';
                message.style.margin = '0';
                message.style.padding = '0';
                
                setTimeout(function() {
                    if (message.parentNode) {
                        message.remove();
                    }
                }, 500);
            });
        }
        
        // Auto-hide success messages after 5 seconds
        if (message.classList.contains('alert-success')) {
            setTimeout(function() {
                if (message.parentNode) {
                    message.style.transition = 'all 0.5s ease';
                    message.style.opacity = '0';
                    setTimeout(function() {
                        if (message.parentNode) {
                            message.remove();
                        }
                    }, 500);
                }
            }, 5000);
        }
    });
    
    console.log('Message handling initialized for ' + messages.length + ' messages');
}

// Book counter functionality
function initializeBookCounter() {
    const bookItems = document.querySelectorAll('.book-item');
    const bookCount = bookItems.length;
    
    // Create or update book counter
    let counterElement = document.getElementById('book-counter');
    
    if (!counterElement) {
        counterElement = document.createElement('div');
        counterElement.id = 'book-counter';
        counterElement.className = 'book-counter';
        counterElement.style.margin = '10px 0';
        counterElement.style.fontSize = '16px';
        counterElement.style.fontWeight = 'bold';
        counterElement.style.color = '#495057';
        
        // Insert after the h1 or at the beginning of content
        const header = document.querySelector('h1');
        if (header) {
            header.parentNode.insertBefore(counterElement, header.nextSibling);
        }
    }
    
    if (bookCount === 0) {
        counterElement.textContent = 'No books in collection';
        counterElement.style.color = '#6c757d';
    } else {
        counterElement.textContent = 'Total Books: ' + bookCount;
        counterElement.style.color = '#28a745';
    }
}

// Utility function to simulate JSX-like behavior
function createBookElement(bookData) {
    // This simulates React-like component creation
    var bookElement = document.createElement('div');
    bookElement.className = 'book-item';
    bookElement.setAttribute('data-book-id', bookData.id);
    
    bookElement.innerHTML = 
        '<div class="row align-items-center">' +
            '<div class="col-md-8">' +
                '<h5 class="mb-1">' + bookData.title + '</h5>' +
                '<p class="mb-0 text-muted">by ' + bookData.author + '</p>' +
            '</div>' +
            '<div class="col-md-4 text-end">' +
                '<span class="badge bg-light text-dark">ID: ' + bookData.id + '</span>' +
            '</div>' +
        '</div>';
    
    return bookElement;
}

// Global function to view book details (can be called from HTML)
function viewBookDetails(bookId) {
    console.log('Viewing book details for ID: ' + bookId);
    window.location.href = '/book-outlet/books/' + bookId + '/';
}

// Export functions for global access (simulating module exports)
if (typeof window !== 'undefined') {
    window.BookOutlet = {
        createBookElement: createBookElement,
        viewBookDetails: viewBookDetails,
        initializeBookInteractions: initializeBookInteractions
    };
}

console.log('BookOutlet JavaScript module loaded');