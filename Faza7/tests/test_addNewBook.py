from django.test import TestCase, Client
from django.urls import reverse
from .models import Book, Author, UsernamesPasswords
from .models import *

class AddNewBookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UsernamesPasswords.objects.create(username='testuser', password='testpassword', email='test@example.com')

        # Create an author show
        author_show = AuthorShow.objects.create(name='John', surname='Doe', bioShow='A talented author')

        # Create an author using the user and author show
        author = Author.objects.create(idUserAuth=self.user, idAuthor=author_show, bio='A successful author')
        self.client.login(username='testuser', password='testpassword')


    # def test_add_new_book_view(self):
    #         response = self.client.get(reverse('addNewBook'))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTemplateUsed(response, 'addNewBook/addNewBook.html')

    def test_add_book_to_database(self):
        data = {
            'bookName': 'Test Book',
            'genre': 'Test Genre',
            'description': 'Test Description',
            # Add other required fields here
        }
        response = self.client.post(reverse('addBookToDataBase'), data)
        # self.assertEqual(response.status_code, 302)  # Expect a redirect
        # self.assertRedirects(response, '/user/{}/'.format(self.user.idUser))
        #
        # Verify that the book is saved in the database
        book = Book.objects.get(title='Test Book')
        self.assertEqual(book.genre, 'Test Genre')
        self.assertEqual(book.description, 'Test Description')
        # # Add more assertions for other fields if necessary

        # # Verify the association between the author and the book
        # author = Author.objects.get(idUserAuth=self.user.idUser)
        # self.assertEqual(author.idAuthor, book.author.idAuthor)
        #
        # # Clean up the test data
        # book.delete()

