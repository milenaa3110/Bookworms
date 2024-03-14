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



from django.core.files import File



# @login_required
def bookView(request, book_title):
    try:
        book = Book.objects.get(title=book_title)
        reviews = listReviews(book.idBook)



        redirect_url = f'/book/{book.idBook}/'
        return redirect(redirect_url)

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
                'coverImage': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "/images/closedBook.jpg",
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
        return redirect(redirect_url)



def listReviews(book_id):
    reviews=[]
    # book = Book.objects.get(idBook=book_id)
    # reviews = book.reviews.all()
    reviews = Reviews.objects.filter(idBook__idBook=book_id)
    print(reviews)

    return reviews



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

def create_review(request, bookId, bookTitle):
    if request.method == 'POST':
        text = request.POST.get("reviewTekst", "aaa")
        print(text)

        book=Book.objects.get(idBook=bookId)

        review = Reviews(
            reviewText=text,
            idUser=request.user,
            idBook=book
        )
        review.save()

        redirect_url = f'/bookPage/{bookTitle}'

    return redirect(redirect_url)

def book(request, bookId):
    book = Book.objects.get(idBook=bookId)
    reviews = listReviews(book.idBook)
    wish = WishList.objects.filter(idBook=book, idUser=request.user).exists()
    read= ReadList.objects.filter(idBook=book, idUser=request.user).exists()
    recommend = RecommendationList.objects.filter(idBook=book, idUser=request.user).exists()


    try:
        user_rating = Rating.objects.get(idUser=request.user, idBook=bookId)
    except Rating.DoesNotExist:
        user_rating = None

    liked_reviews = Reaction.objects.filter(idUser=request.user, type='like')
    liked_review_ids = [Reaction.idReview_id for Reaction in liked_reviews]
    disliked_reviews =  Reaction.objects.filter(idUser=request.user, type='dislike')
    disliked_review_ids = [Reaction.idReview_id for Reaction in disliked_reviews]
    print(liked_review_ids)
    context = {'book': book, 'reviews': reviews, 'user_rating' : user_rating, 'liked_review_ids': liked_review_ids, 'disliked_review_ids': disliked_review_ids, 'wish':wish, 'read':read, 'recommend':recommend }
    return render(request, 'bookPage/bookPage.html/', context)


def add_to_wishlist(request, book_id):
    if request.method == 'POST':
        # Logic to add the book to the wish list
        # Retrieve the book object using the book_id
        book = Book.objects.get(idBook=book_id)
        # Add the book to the user's wish list (assuming you have a WishList model)
        des_user_id = request.user
        try:
            wishlist_item = WishList.objects.get(idUser=des_user_id, idBook=book)
            wishlist_item.delete()
        except:
            wish_list = WishList(idUser=des_user_id, idBook=book)
            wish_list.save()
        redirect_url = f'/book/{book.idBook}'

        # Redirect the user back to the book page or any other desired page
        return redirect(redirect_url)
    # Handle GET requests or any other method
    return redirect('home')  # Redirect the user to the home page if needed


def add_to_readlist(request, book_id):
    if request.method == 'POST':
        # Logic to add the book to the wish list
        # Retrieve the book object using the book_id
        book = Book.objects.get(idBook=book_id)
        # Add the book to the user's wish list (assuming you have a WishList model)
        des_user_id = request.user

        try:
            readlist_item = ReadList.objects.get(idUser=des_user_id, idBook=book)
            readlist_item.delete()
            #logika za brisanje bedza po potrebi ako je counter pao ispod nekog achievement broja
            readlist_items = ReadList.objects.filter(idUser=des_user_id)
            counter = readlist_items.count()
            badges = HasBadge.objects.filter(idUser=des_user_id)
            badge_ids = badges.values_list("idBadge", flat=True)
            achievements = Achievement.objects.filter(idBadge__in=badge_ids)
            achievements_count = achievements.count()
            if (achievements_count == 1):
                if (counter == 0):
                    # dodavanje bedza korisniku
                    achievement = Achievement.objects.filter(numberOfBooks=1)
                    achievement_badgeId = achievement.values_list("idBadge", flat=True)
                    badge = Badge.objects.get(idBadge=achievement_badgeId[0])
                    hasBadge_item = HasBadge.objects.get(idBadge=badge, idUser=des_user_id)
                    hasBadge_item.delete()
            elif (achievements_count == 2):
                if (counter == 4):
                    # dodavanje bedza korisniku
                    achievement = Achievement.objects.filter(numberOfBooks=5)
                    achievement_badgeId = achievement.values_list("idBadge", flat=True)
                    badge = Badge.objects.get(idBadge=achievement_badgeId[0])
                    hasBadge_item = HasBadge.objects.get(idBadge=badge, idUser=des_user_id)
                    hasBadge_item.delete()
            elif (achievements_count == 3):
                if (counter == 9):
                    # dodavanje bedza korisniku
                    achievement = Achievement.objects.filter(numberOfBooks=10)
                    achievement_badgeId = achievement.values_list("idBadge", flat=True)
                    badge = Badge.objects.get(idBadge=achievement_badgeId[0])
                    hasBadge_item = HasBadge.objects.get(idBadge=badge, idUser=des_user_id)
                    hasBadge_item.delete()



            #logika za uklanjanje bedza za challenge
            user_id = des_user_id
            takes_challenges = TakesChallenge.objects.all().filter(idUser=user_id, idChallenge__status="true")
            readlist = ReadList.objects.all().filter(idUser=user_id)
            readlist_booksids = readlist.values_list("idBook", flat=True)
            if takes_challenges.values_list("idChallenge", flat=True).count() != 0:
                takes_challenges_id = takes_challenges.values_list("idChallenge", flat=True)
                for id in takes_challenges_id:
                    badgei = Challenge.objects.filter(idChallenge=id)
                    badgeid = badgei.values_list("idBadge", flat=True)
                    print(badgeid[0])
                    hasBadge_item = HasBadge.objects.filter(idBadge=badgeid[0], idUser=user_id)
                    if(hasBadge_item.count() != 0):
                        challengebooks = ChallengeBooks.objects.filter(idChallenge=id)
                        challengebooks = challengebooks.filter(idBook__in=readlist_booksids)
                        if challengebooks.values_list("idBook", flat=True).count() != 3:
                            hasBadge_item.delete()

        except:
            read_list = ReadList(idUser=des_user_id, idBook=book)
            read_list.save()
            #logika za dodavanje bedza po potrebi ako je counter presao neki milestone
            readlist_items = ReadList.objects.filter(idUser=des_user_id)
            counter = readlist_items.count()
            badges = HasBadge.objects.filter(idUser=des_user_id)
            badge_ids = badges.values_list("idBadge", flat=True)
            achievements = Achievement.objects.filter(idBadge__in=badge_ids)
            achievements_count = achievements.count()
            if(achievements_count == 0):
                if(counter == 1):
                    # dodavanje bedza korisniku
                    achievement = Achievement.objects.filter(numberOfBooks=1)
                    achievement_badgeId = achievement.values_list("idBadge", flat=True)
                    badge = Badge.objects.get(idBadge=achievement_badgeId[0])
                    hasBadge_item = HasBadge(idBadge=badge, idUser=des_user_id)
                    hasBadge_item.save()
            elif(achievements_count == 1):
                if(counter == 5):
                    # dodavanje bedza korisniku
                    achievement = Achievement.objects.filter(numberOfBooks=5)
                    achievement_badgeId = achievement.values_list("idBadge", flat=True)
                    badge = Badge.objects.get(idBadge=achievement_badgeId[0])
                    hasBadge_item = HasBadge(idBadge=badge, idUser=des_user_id)
                    hasBadge_item.save()
            elif(achievements_count == 2):
                if(counter == 10):
                    # dodavanje bedza korisniku
                    achievement = Achievement.objects.filter(numberOfBooks=10)
                    achievement_badgeId = achievement.values_list("idBadge", flat=True)
                    badge = Badge.objects.get(idBadge=achievement_badgeId[0])
                    hasBadge_item = HasBadge(idBadge=badge, idUser=des_user_id)
                    hasBadge_item.save()

            #logika za dodavanje bedza za challenge
            user_id = des_user_id
            takes_challenges = TakesChallenge.objects.all().filter(idUser=user_id, idChallenge__status="true")
            readlist = ReadList.objects.all().filter(idUser=user_id)
            readlist_booksids = readlist.values_list("idBook", flat=True)
            if takes_challenges != None:
                takes_challenges_id = takes_challenges.values_list("idChallenge", flat=True)
                for id in takes_challenges_id:
                    challengebooks = ChallengeBooks.objects.filter(idChallenge=id)
                    challengebooks = challengebooks.filter(idBook__in=readlist_booksids)
                    if challengebooks.values_list("idBook", flat=True).count() == 3:
                        clg = Challenge.objects.filter(idChallenge=id)
                        badgeids = clg.values_list("idBadge", flat=True)
                        badge = Badge.objects.get(idBadge=badgeids[0])
                        if (HasBadge.objects.filter(idBadge=badge, idUser=user_id).count() == 0):
                            hasBadge_item = HasBadge(idBadge=badge, idUser=user_id)
                            hasBadge_item.save()


        redirect_url = f'/book/{book.idBook}'

        # Redirect the user back to the book page or any other desired page
        return redirect(redirect_url)
    # Handle GET requests or any other method
    return redirect('home')  # Redirect the user to the home page if needed

def add_to_recommended(request, book_id):
    if request.method == 'POST':
        # Logic to add the book to the wish list
        # Retrieve the book object using the book_id
        book = Book.objects.get(idBook=book_id)
        # Add the book to the user's wish list (assuming you have a WishList model)
        des_user_id = request.user

        try:
            recommended_item = RecommendationList.objects.get(idUser=des_user_id, idBook=book)
            recommended_item.delete()
        except:
            recommend_list = RecommendationList(idUser=des_user_id, idBook=book)
            recommend_list.save()

        redirect_url = f'/book/{book.idBook}'

        # Redirect the user back to the book page or any other desired page
        return redirect(redirect_url)
    # Handle GET requests or any other method
    return redirect('home')  # Redirect the user to the home page if needed