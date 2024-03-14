from django.test import TestCase, Client
from django.urls import reverse
from .models import UsernamesPasswords, User, AuthorShow, Author


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_user(self):
        # Simulate a POST request to register a user
        response = self.client.post(self.register_url, {
            'form_type': 'user',
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'testuser@example.com',
            # Provide other required form data as needed
        })

        # Check if the registration was successful
        self.assertEqual(response.status_code, 200)

        # Check if the user was created in the database
        user_exists = UsernamesPasswords.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)

        # Optionally, you can also check if the user was redirected to the home page
        # self.assertRedirects(response, reverse('home'))

    # def test_register_author(self):
    #     author_show = AuthorShow.objects.create(name='John', surname='Doe', bioShow='Sample Bio')
    #     author = Author.objects.create(idAuthor=author_show, bio='Author Bio')
    #     author_exists = Author.objects.filter(idAuthor=author.idAuthor).exists()
    #     self.assertTrue(author_exists)

