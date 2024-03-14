from django.test import TestCase
from .models import *


class newUser(TestCase):
    def setUp(self):
        UsernamesPasswords.objects.create(username="testUser", password="pass", email='testUser@gmail.com')
        user=UsernamesPasswords.objects.get(username="testUser")
        User.objects.create(idUser=user)

    def testUserRequest(self):
        user = UsernamesPasswords.objects.get(username="testUser")
        user.groups.add(1)
        self.assertTrue(user.email, 'testUser@gmail.com')


