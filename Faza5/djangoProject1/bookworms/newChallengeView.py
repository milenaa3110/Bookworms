import json
import random
import os
import uuid

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
import requests
from django import forms
from django.http import HttpResponse

# Create your views here.
from django.shortcuts import render, redirect

from djangoProject1 import settings
from .models import *

import datetime


def addNewChallenge(request):
    if request.method == 'POST':
        challengeName = request.POST.get("challengeName")
        challengeDescription=request.POST.get("challengeDescription")
        endDate =request.POST.get("endDate")
        challengeImg = request.POST.get("challengeImg")
        book1Title = request.POST.get("book1Title")
        # book2Title = request.POST.get("book2Title")
        # book3Title = request.POST.get("book3Title")
        #
        image_file = request.FILES.get('image')


        imgPath = "/images/clg3.jpg"
        startDate=datetime.date.today()

        book1=getBookForChallenge(book1Title)

        badgeModel = Badge(description=imgPath)
        badgeModel.save()
        challengeModel = Challenge(name=challengeName, description=challengeDescription,
                                   status="true", idBadge=badgeModel, startDate=startDate, endDate=endDate)
        challengeModel.save()

        challBooksModel1=ChallengeBooks(idBook=book1, idChallenge=challengeModel)
        challBooksModel1.save()




        # bedz tabela? ovde ide slika
        # challenge tabela
        # challengeBooks tabela



    return redirect('home')



def getBookForChallenge(book_title):
    try:
        book = Book.objects.get(title=book_title)
        return book

    except Book.DoesNotExist:

        queries = {'q': book_title, 'title': book_title}
        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params=queries
        )
        if r.status_code != 200:
            return render(request, "search.html")
        data = r.json();
        print(data)

        response_content = r.content
        data = json.loads(response_content)

        fetched_books = data['items']
        books = []
        isbn = 900
        isbn=random.randint(0, 10000)

        for book in fetched_books:
            print(book)
            isbn += 1
            book_dict = {

                'id': book['volumeInfo']['industryIdentifiers'][0]['identifier'] if 'industryIdentifiers' in book['volumeInfo'] else str(isbn),
                'title': book['volumeInfo']['title'],
                'coverImage': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "../../images/closedBook.jpg",
                'authors': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "No Author",
                'description': book['volumeInfo']['description'] if 'description' in book[
                    'volumeInfo'] else "This book has no description",
                'info': book['volumeInfo']['infoLink'],
                'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0,
                'rating': book['volumeInfo']['averageRating'] if 'averageRating' in book['volumeInfo'] else 3,
                'genre' :  book['volumeInfo']['categories'] if 'categories' in book['volumeInfo'] else "fiction",
            }
            books.append(book_dict)

        def sort_by_pop(e):
            return e['popularity']

        books.sort(reverse=True, key=sort_by_pop)

        print(books[0])
        book=books[0]
        newBook = saveBookInDataBase(book)
        redirect_url = f'/book/{newBook.idBook}'
        return newBook


def download_image(url, my_model):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Create a new instance of MyModel
            filename = f'uploaded_image_{uuid.uuid4().hex}.jpg'
            image_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(image_path, 'wb') as file:
                file.write(response.content)
            my_model.coverImage = '/images/'+ filename
            my_model.save()
    except:
        my_model.save()

def saveBookInDataBase(newBook):

        book = Book(

            # idBook=newBook['id'],
            title=newBook['title'],
            genre=newBook['genre'][0],
            description=newBook['description'],
        )
        download_image(newBook['coverImage'], book)
        authors = newBook['authors']
        author_names = authors.split(",");
        for author in author_names:
            author_name_parts = author.split()
            author_name = author_name_parts[0]
            author_surname = ""
            for i in range (1, len(author_name_parts)):
                author_surname += author_name_parts[i] + (" " if i != len(author_name_parts) - 1 else "")
            authorExists = AuthorShow.objects.filter(name = author_name, surname=author_surname)
            if not authorExists:
                newAuthor = AuthorShow(name=author_name, surname=author_surname, bioShow="")
                newAuthor.save()
                authorWrote = AuthorWroteBook(idBook=book, idAuthor=newAuthor)
                authorWrote.save()
            else:
                author = AuthorShow.objects.get(name=author_name, surname=author_surname)
                authorWrote = AuthorWroteBook(idBook=book, idAuthor=author)
                authorWrote.save()
        return book;