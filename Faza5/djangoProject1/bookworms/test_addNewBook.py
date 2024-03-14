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
        self.client.force_login(self.user)
        print(author)

        def test_add_new_book_view(self):
            response = self.client.get(reverse('add_new_book'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'addNewBook/addNewBook.html')



    def test_add_book_to_database(self):
        url = reverse('addBookToDataBase')
        book_data = {
            'bookName': 'Test Book',
            'genre': 'Fiction',
            'description': 'This is a test book',
        }

        response = self.client.post(url, data=book_data, follow=True)

        self.assertRedirects(response, f'/user/{self.user.idUser}/')

        # Check if the book was saved in the database
        book = Book.objects.get(title='Test Book')
        self.assertEqual(book.title, 'Test Book')
        self.assertEqual(book.genre, 'Fiction')
        self.assertEqual(book.description, 'This is a test book')

        # Check if the book is associated with the author
        au = Author.objects.get(idUserAuth=self.user)

        author_wrote_book = AuthorWroteBook.objects.get(idBook=book)
        self.assertEqual(author_wrote_book.idAuthor, au.idAuthor)

