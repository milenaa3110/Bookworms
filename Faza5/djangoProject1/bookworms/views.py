import uuid
import datetime
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import os

from django.db.models import Avg
from django.http import JsonResponse
# Create your views here.
from django.shortcuts import render, redirect

from djangoProject1 import settings
from .models import *
from .forms import UserForm, UserDetailForm, RequestForm, LoginForm
from django.contrib.auth.views import LogoutView


def register(request):
    user_form = UserForm()
    user_detail_form = UserDetailForm()
    author_form = UserForm()
    author_detail_form = UserDetailForm()
    request_form = RequestForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'user':
            user_form = UserForm(request.POST)
            user_detail_form = UserDetailForm(request.POST)

            if user_form.is_valid() and user_detail_form.is_valid():
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.save()
                user.groups.add(1)
                user_detail = user_detail_form.save(commit=False)
                user_detail.idUser = user
                user_detail.save()


        elif form_type == 'author':
            author_form = UserForm(request.POST)
            request_form = RequestForm(request.POST)
            author_detail_form = UserDetailForm(request.POST)
            if author_form.is_valid() and request_form.is_valid() and author_detail_form.is_valid():
                author_user = author_form.save(commit=False)
                author_user.set_password(author_form.cleaned_data['password'])
                author_user.save()
                author_user.groups.add(1)
                author_detail = author_detail_form.save(commit=False)
                author_detail.idUser = author_user
                author_detail.save()
                new_request = request_form.save(commit=False)
                new_request.idUser = author_detail
                new_request.type = "author"
                new_request.save()

    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'user_detail_form': user_detail_form,
        'author_form': author_form,
        'author_detail_form': author_detail_form,
        'request_form': request_form
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form': form})


@login_required
def home(request):
    if request.user.is_superuser:
        authorRequests = Request.objects.all().filter(type="author");
        reviewerRequests = Request.objects.all().filter(type="reviewer");
        return render(request, 'user/adminPage.html',
                      {"authorRequests": authorRequests, "reviewerRequests": reviewerRequests})

    #upadate status-a za challenge
    challenges = Challenge.objects.all()
    for challenge in challenges:
        if challenge.endDate < datetime.date.today():
            challenge.status = "false"
            challenge.save()

    #logika za challenge-e
    user_id = request.user
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



    romanceBooks = Book.objects.all().filter(genre="romance");
    classicBooks = Book.objects.all().filter(genre="classic");
    psychologyBooks = Book.objects.all().filter(genre="psychology");
    return render(request, 'home/homePage.html',
                  {'romanceBooks': romanceBooks, 'classicBooks': classicBooks, 'psychologyBooks': psychologyBooks})


def challengeList(request):
    challenges = Challenge.objects.all().filter(endDate__gt=datetime.date.today())
    return render(request, 'challenges/challengeListPage.html', {'challenges': challenges})


def challengePage(request, object_id):
    challenge = Challenge.objects.all().filter(idChallenge=object_id)
    book_ids = ChallengeBooks.objects.all().filter(idChallenge=object_id)
    books = Book.objects.all().filter(idBook__in=book_ids.values_list("idBook", flat=True))
    return render(request, 'challenges/challengeProfile.html', {'books': books, 'challenge': challenge})


def intro(request):
    return render(request, 'intro/intro.html')


@login_required
def user(request, des_user_id):
    des_user = UsernamesPasswords.objects.get(idUser=des_user_id)
    if des_user.is_superuser:

        authorRequests = Request.objects.all().filter(type="author");
        reviewerRequests = Request.objects.all().filter(type="reviewer");
        return render(request, 'user/adminPage.html',
                      {"authorRequests": authorRequests, "reviewerRequests": reviewerRequests})
    elif des_user.groups.filter(id=3):
        readlist = ReadList.objects.filter(idUser=des_user)
        book_ids = readlist.values_list('idBook', flat=True)
        readlist_books = Book.objects.filter(idBook__in=book_ids)
        wishlist = WishList.objects.filter(idUser=des_user)
        book_ids = wishlist.values_list('idBook', flat=True)
        wishlist_books = Book.objects.filter(idBook__in=book_ids)
        recommendationList = RecommendationList.objects.filter(idUser=des_user)
        book_ids = recommendationList.values_list('idBook', flat=True)
        recommendationlist_books = Book.objects.filter(idBook__in=book_ids)
        author = Author.objects.get(idUserAuth=des_user)
        bookList = AuthorWroteBook.objects.filter(idAuthor=author.idAuthor)
        book_ids = bookList.values_list('idBook', flat=True)
        written_books = Book.objects.filter(idBook__in=book_ids)
        badges_list = HasBadge.objects.filter(idUser=des_user)
        badges_ids = badges_list.values_list('idBadge', flat=True)
        badges = Badge.objects.filter(idBadge__in=badges_ids)
        return render(request, 'user/authorProfilePage.html',
                      {"des_user": des_user, "readlist_books": readlist_books, "wishlist_books": wishlist_books,
                       "recommendationlist_books": recommendationlist_books, "author": author,
                       "written_books": written_books, "badges": badges})
    elif des_user.groups.filter(id=2):
        readlist = ReadList.objects.filter(idUser=des_user)
        book_ids = readlist.values_list('idBook', flat=True)
        readlist_books = Book.objects.filter(idBook__in=book_ids)
        wishlist = WishList.objects.filter(idUser=des_user)
        book_ids = wishlist.values_list('idBook', flat=True)
        wishlist_books = Book.objects.filter(idBook__in=book_ids)
        recommendationList = RecommendationList.objects.filter(idUser=des_user)
        book_ids = recommendationList.values_list('idBook', flat=True)
        recommendationlist_books = Book.objects.filter(idBook__in=book_ids)
        reviewer = Reviewer.objects.get(idUserRew=des_user)
        badges_list = HasBadge.objects.filter(idUser=des_user)
        badges_ids = badges_list.values_list('idBadge', flat=True)
        badges = Badge.objects.filter(idBadge__in=badges_ids)
        return render(request, 'user/reviewerProfilePage.html',
                      {"des_user": des_user, "readlist_books": readlist_books, "wishlist_books": wishlist_books,
                       "recommendationlist_books": recommendationlist_books, "reviewer": reviewer, "badges": badges})
    else:
        readlist = ReadList.objects.filter(idUser=des_user)
        book_ids = readlist.values_list('idBook', flat=True)
        readlist_books = Book.objects.filter(idBook__in=book_ids)
        wishlist = WishList.objects.filter(idUser=des_user)
        book_ids = wishlist.values_list('idBook', flat=True)
        wishlist_books = Book.objects.filter(idBook__in=book_ids)
        return render(request, 'user/userProfilePage.html',
                      {"des_user": des_user, "readlist_books": readlist_books, "wishlist_books": wishlist_books})


class customLogoutView(LogoutView):
    next_page = '/login/'


def upgrade_request(request):
    user = request.user
    des_user = User.objects.get(idUser=user)
    des_user_id = request.user.idUser
    redirect_url = f'/user/{des_user_id}'
    request_exists = Request.objects.filter(idUser=des_user).exists()
    if (request_exists):
        return redirect(redirect_url)
    new_request = Request(idUser=des_user, type="reviewer")
    new_request.save()
    return redirect(redirect_url)


def approve_request(request, idRequest):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        des_user_id = request.user.idUser
        redirect_url = f'/user/{des_user_id}'
        app_request = Request.objects.get(idRequest=idRequest)
        if (app_request.type == "reviewer"):
            reviewer = Reviewer(idUserRew=app_request.idUser.idUser, bio="")
            reviewer.save()
            app_request.idUser.idUser.groups.add(2)
            app_request.idUser.delete()
            app_request.delete()
            return JsonResponse({"redirect_url": redirect_url})
        else:
            authorshow_exists = AuthorShow.objects.filter(name=app_request.name, surname=app_request.surname).exists()
            if (authorshow_exists):
                authorshow_objects = AuthorShow.objects.filter(name=app_request.name, surname=app_request.surname)
                authorshow_id = authorshow_objects.first()
            else:
                authorshow_id = AuthorShow(name=app_request.name, surname=app_request.surname, bioShow="")
                authorshow_id.save()
            author = Author(idAuthor=authorshow_id, idUserAuth=app_request.idUser.idUser, bio=authorshow_id.bioShow)
            author.save()
            app_request.idUser.idUser.groups.add(3)
            app_request.idUser.delete()
            app_request.delete()
            return JsonResponse({"redirect_url": redirect_url})
    else:
        return JsonResponse({"error": "Invalid Ajax POST request"})


def delete_request(request, idRequest):
    des_user_id = request.user.idUser
    redirect_url = f'/user/{des_user_id}'

    if request.method == 'POST':
        try:
            app_request = Request.objects.get(idRequest=idRequest)
            app_request.delete()
            return JsonResponse({'message': 'Request deleted successfully.'})
        except Request.DoesNotExist:
            return JsonResponse({'error': 'Request not found.'}, status=400)
    else:
        return redirect(redirect_url)


def edit_page(request):
    user = request.user
    des_user_id = request.user.idUser
    des_user = UsernamesPasswords.objects.get(idUser=des_user_id)
    username = UsernamesPasswords.objects.get(idUser=des_user_id)  # dohvatamo username sa nasim id


    if (des_user.groups.filter(id=3)):
        bio = Author.objects.get(idUserAuth=des_user_id)  # dohvatamo odgovarajucu biografiju
        recommendationList = RecommendationList.objects.filter(idUser=des_user_id)
        book_ids = recommendationList.values_list('idBook', flat=True)  # uzimamo ids svih knjiga u listi
        recommendationList_books = Book.objects.filter(idBook__in=book_ids)  # dohvatamo objekte knjiga
        return render(request, 'edit/editAuthors.html', {
            'username': username,
            'bio': bio,
            'recommendationList_books': recommendationList_books
        })
    elif (des_user.groups.filter(id=2)):
        bio = Reviewer.objects.get(idUserRew=des_user_id)  # dohvatamo odgovarajucu biografiju
        recommendationList = RecommendationList.objects.filter(idUser=des_user_id)
        book_ids = recommendationList.values_list('idBook', flat=True)  # uzimamo ids svih knjiga u listi
        recommendationList_books = Book.objects.filter(idBook__in=book_ids)  # dohvatamo objekte knjiga
        return render(request, 'edit/editReviewer.html', {
            'username': username,
            'bio': bio,
            'recommendationList_books': recommendationList_books
        })
    elif(des_user.groups.filter(id=1)):
        return render(request, 'edit/editUser.html', {
            'username': username
        })

def edit(request):
    des_user_id = request.user.idUser
    des_user = UsernamesPasswords.objects.get(idUser=des_user_id)
    redirect_url = f'/user/{des_user_id}'
    image_file = request.FILES.get('image')

    if request.method == 'POST':
        print("usli smo")
        new_username = request.POST.get('newUsername')  # iz requesta uzimamo info o novom username-u/ bio
        new_bio = request.POST.get('newBio')

        user = UsernamesPasswords.objects.get(idUser=des_user_id)  # dohvatamo username sa nasim id
        if (des_user.groups.filter(id=2)):
            bio = Reviewer.objects.get(idUserRew=des_user_id)  # dohvatamo odgovarajucu biografiju
        elif(des_user.groups.filter(id=3)):
            bio = Author.objects.get(idUserAuth=des_user_id)

        if (user != None):  # u slucaju da je nesto uneseno u polje za promenu korisnickog imena, postavljamo novo ime
            user.username = new_username
            user.save()
        if (bio != None):  # u slucaju da je nesto uneseno u polje za promenu biografije, postavljamo novi bip
            bio.bio = new_bio
            bio.save()
        if image_file:
            # Generate a unique filename for the uploaded image
            filename = f'uploaded_image_{uuid.uuid4().hex}.jpg'

            # Save the uploaded image to the media directory
            image_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(image_path, 'wb') as file:
                for chunk in image_file.chunks():
                    file.write(chunk)
            request.user.profileImage = "/images/" + filename
            request.user.save()

    return redirect(redirect_url)


def editUser(request):
    des_user_id = request.user.idUser
    redirect_url = f'/user/{des_user_id}'
    image_file = request.FILES.get('image')

    if request.method == 'POST':
        print("usli smo")
        new_username = request.POST.get('newUsername')  # iz requesta uzimamo info o novom username-u/ bio


        user = UsernamesPasswords.objects.get(idUser=des_user_id)  # dohvatamo username sa nasim id

        if (user != None):  # u slucaju da je nesto uneseno u polje za promenu korisnickog imena, postavljamo novo ime
            user.username = new_username
            user.save()

    return redirect(redirect_url)

def bookRemove(request, book_id):
    redirect_url = f'/edit_page/'
    reccomentation = RecommendationList.objects.get(idBook=book_id, idUser=request.user.idUser)
    reccomentation.delete()
    return redirect(redirect_url)


def author_show_page(request, idAuthor):
    author = AuthorShow.objects.get(idAuthor=idAuthor)
    written_books = Book.objects.filter(authorwrotebook__idAuthor=author)
    return render(request, "authorshow/authorShowPage.html", {"author": author, "written_books": written_books})


def author_clicked(request, idAuthor):
    author = Author.objects.filter(idAuthor=idAuthor)
    des_user_id = request.user.idUser
    if (author):  # ako postoji autor ide se na njegovu stranicu
        s_author = Author.objects.get(idAuthor=idAuthor)
        redirect_url = f'/user/{s_author.idUserAuth_id}'
        return redirect(redirect_url)
    else:  # ako ne postoji ide se na stranicu prikaznog autora
        redirect_url = f'/author_show_page/{idAuthor}'
        return redirect(redirect_url)


def apply(request, challengeId):
    print("pls")
    user_id = request.user
    challenge = Challenge.objects.get(idChallenge=challengeId)
    redirect_url = f'/home/'
    if request.method == "POST":
        model = TakesChallenge(
            idUser=user_id,
            idChallenge=challenge
        )
        model.save()

    return redirect(redirect_url)


def rate_book(request, idBook):
    try:
        book = Book.objects.get(idBook=idBook)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)
    rating_value = request.POST.get('rating')
    Rating.objects.filter(idUser=request.user).delete()
    new_rating = Rating(rating = rating_value, idBook=book, idUser=request.user)
    new_rating.save()
    ratings = Rating.objects.filter(idBook=book)
    rating_sum = sum([rating.rating for rating in ratings])
    rating_count = ratings.count()

    if rating_count > 0:
        average_rating = rating_sum / rating_count
    else:
        average_rating = 0
    book.rating_fin = average_rating
    book.save()
    return JsonResponse({'rating': average_rating})

def add_reaction(request):
    reaction = request.POST.get('reaction')
    idReview = request.POST.get('idReview')
    try:
        review = Reviews.objects.get(idReview=idReview)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Review not found'}, status=404)
    try:
        reaction_des = Reaction.objects.get(idReview=idReview, idUser=request.user)
        if (reaction_des.type=="like"):
            if (reaction=="like"):
                return JsonResponse({'likes': review.likes, 'dislikes': review.dislikes})
            review.likes= review.likes-1
            review.dislikes = review.dislikes + 1
            review.save()
            reaction_des.type = reaction
            reaction_des.save()
            return JsonResponse({'likes': review.likes, 'dislikes': review.dislikes})
        else:
            if (reaction=="dislike"):
                return JsonResponse({'likes': review.likes, 'dislikes': review.dislikes})
            review.dislikes=review.dislikes - 1
            review.likes = review.likes + 1
            review.save()
            reaction_des.type = reaction
            reaction_des.save()
            return JsonResponse({'likes': review.likes, 'dislikes': review.dislikes})
    except:
        reaction_des = Reaction(idUser=request.user, idReview=review, type = reaction)
        if (reaction_des.type=="like"):
            review.likes= review.likes+1
            review.save()
            reaction_des.save()
            return JsonResponse({'likes': review.likes, 'dislikes': review.dislikes})
        else:
            review.dislikes=review.dislikes+1
            review.save()
            reaction_des.save()
            return JsonResponse({'likes': review.likes, 'dislikes': review.dislikes})
