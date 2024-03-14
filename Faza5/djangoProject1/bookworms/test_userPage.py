from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserProfileTest(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

    def test_user_profile_page(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Retrieve the user profile page URL
        url = reverse('user', args=[self.user.idUser])

        # Send a GET request to the user profile page URL
        response = self.client.get(url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected content
        self.assertContains(response, 'edit profile')
        self.assertContains(response, self.user.username)
        # self.assertContains(response, self.user.email)
