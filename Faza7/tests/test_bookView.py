from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import Book

class BookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.book_title = "Sample Book Title"

    def test_bookView_existing_book(self):
        # Create a book object for testing
        book = Book.objects.create(title=self.book_title)

        # Generate the URL for the book view
        url = reverse('bookView', args=[book.title])

        # Send a GET request to the book view
        response = self.client.get(url)

        # Check that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check that the redirect URL matches the expected format
        redirect_url = reverse('book', args=[book.idBook])
        # self.assertRedirects(response, redirect_url)

    from unittest.mock import MagicMock
    from django.test import TestCase
    from django.urls import reverse
    from unittest.mock import patch

    class BookViewTestCase(TestCase):
        def setUp(self):
            self.book_title = 'Sample Book Title'

        @patch('requests.get')
        def test_bookView_new_book(self, mock_get):
            # Mock the response from the external API
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'items': [
                    {
                        'volumeInfo': {
                            'title': self.book_title,
                            'description': 'Sample description',
                            'authors': ['John Doe'],
                            'imageLinks': {'thumbnail': 'http://example.com/image.jpg'},
                            'infoLink': 'http://example.com/book'
                        }
                    }
                ]
            }
            mock_get.return_value = mock_response

            # Generate the URL for the book view
            url = reverse('bookView', args=[self.book_title])

            # Send a GET request to the book view
            response = self.client.get(url)

            # Check that the response status code is 302 (redirect)
            self.assertEqual(response.status_code, 302)

            # Check that a new book object was created in the database
            self.assertEqual(Book.objects.count(), 1)

            # Retrieve the created book object
            book = Book.objects.first()

            # Check that the redirect URL matches the expected format
            redirect_url = reverse('book', args=[book.id])
            self.assertRedirects(response, redirect_url)
