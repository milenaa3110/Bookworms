from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
import requests
from django import forms
from django.http import HttpResponse
import os
import uuid
from django.core.files.images import ImageFile



# Create your views here.
from django.shortcuts import render, redirect

from djangoProject1 import settings
from .models import *
from .bookView import saveBookInDataBase


def addNewBook(request):
    return render(request, "addNewBook/addNewBook.html")

# @login_required
def addBookToDataBase(request):
    des_user_id = request.user.idUser
    redirect_url = f'/user/{des_user_id}'

    if request.method == 'POST':
        newBookName=request.POST.get("bookName")
        newGenre=request.POST.get("genre")
        newDescription = request.POST.get("description")
        image_file = request.FILES.get('image')
        # cover_image= os.path.join(settings.MEDIA_ROOT, 'closedBook.jpg')
        cover_image="/images/closedBook.jpg"

        if image_file:
            # Generate a unique filename for the uploaded image
            filename = f'uploaded_image_{uuid.uuid4().hex}.jpg'

            # Save the uploaded image to the media directory
            image_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(image_path, 'wb') as file:
                for chunk in image_file.chunks():
                    file.write(chunk)
            cover_image= "/images/" + filename
        else:
            print (newGenre)
            print("uslao u else")



        book = Book(
            # idBook=newBook['id'],
            title=newBookName,
            genre=newGenre,
            description=newDescription,
            coverImage=cover_image,
        )
        book.save()
        author=Author.objects.get(idUserAuth=des_user_id)
        idAuthor=author.idAuthor


        bookFromDataBase=Book.objects.get(title=newBookName)
        # if(bookFromDataBase.length>1):
        #     bookFromDataBase=bookFromDataBase[-1]

        myModel = AuthorWroteBook(
            idAuthor=idAuthor,
            idBook=bookFromDataBase
        )
        myModel.save()

    return redirect(redirect_url)