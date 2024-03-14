from django.test import TestCase
from .models import *

class adminUserRequestCase(TestCase):
    def setUp(self):
       user=UsernamesPasswords.objects.create(username="testUser", password="pass", email='testUser@gmail.com')
       user.groups.add(1)
       newUser=User.objects.create(idUser=user)
       Request.objects.create(idUser=newUser, type="reviewer")


    def testUserRequest(self):
        app_request = Request.objects.get(type="reviewer")
        des_user =UsernamesPasswords.objects.get(idUser=app_request.idUser.idUser.idUser)
        if (app_request.type == "reviewer"):
            reviewer = Reviewer(idUserRew=app_request.idUser.idUser, bio="")
            reviewer.save()
            des_user.groups.add(2)
            des_user.save()

            self.assertIsNotNone(app_request)
            self.assertIsInstance(app_request.idUser, User)
            self.assertIsNotNone(reviewer)
            self.assertEqual(reviewer.idUserRew.idUser, app_request.idUser.idUser.idUser)
            # self.assertTrue(des_user.groups.filter(id=2).exists())

            testUser=UsernamesPasswords.objects.get(idUser=app_request.idUser.idUser.idUser)

            app_request.idUser.delete()
            app_request.delete()



            self.assertFalse(Request.objects.filter(idRequest=app_request.idRequest).exists())
            # self.assertFalse(UsernamesPasswords.objects.filter(idUser=app_request.idUser).exists())
            # self.assertFalse(UsernamesPasswords.objects.filter(idUser=testUser.idUser).exists())




class adminAuthorRequestCase(TestCase):

    def setUp(self):
        user = UsernamesPasswords.objects.create(username="testUser", password="pass", email='testUser@gmail.com')
        user.groups.add(1)
        newUser = User.objects.create(idUser=user)
        Request.objects.create(idUser=newUser, type="author")

    def testUserRequest(self):
        app_request = Request.objects.get(type="author")
        des_user = UsernamesPasswords.objects.get(idUser=app_request.idUser.idUser.idUser)
        if (app_request.type == "author"):
            authorShow = AuthorShow( name="Auhtor", surname="author")
            authorShow.save()
            author=Author(idUserAuth=app_request.idUser.idUser,idAuthor=authorShow)
            author.save()
            des_user.groups.add(2)
            des_user.save()

            self.assertIsNotNone(app_request)
            self.assertIsInstance(app_request.idUser, User)
            self.assertIsNotNone(author)
            self.assertEqual(author.idUserAuth.idUser, app_request.idUser.idUser.idUser)
            # self.assertTrue(des_user.groups.filter(id=2).exists())

            testUser = UsernamesPasswords.objects.get(idUser=app_request.idUser.idUser.idUser)

            app_request.idUser.delete()
            app_request.delete()

            self.assertFalse(Request.objects.filter(idRequest=app_request.idRequest).exists())
            # self.assertFalse(UsernamesPasswords.objects.filter(idUser=app_request.idUser).exists())
            # self.assertFalse(UsernamesPasswords.objects.filter(idUser=testUser.idUser).exists())






