from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from .bookView import *
from .searchResultView  import *
from .addNewBookView import *
from .newChallengeView import *

urlpatterns = [
    path('', intro, name='intro'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
    path('user/<int:des_user_id>/', user, name='user'),
    path('logout/', customLogoutView.as_view(), name='logout'),
    path('upgrade_request/', upgrade_request, name = 'upgrade_request'),
    path('approve_request/<int:idRequest>/', approve_request, name = 'approve_request'),
    path('delete_request/<int:idRequest>/', delete_request, name = 'delete_request'),
    path('edit_page/', edit_page, name = 'edit_page'),
    path('edit/', edit, name = 'edit'),
    path('searchResult/<str:searchInput>/', search, name='search'),
    path('bookPage/<str:book_title>/', bookView, name='bookView'),
    path('create_review/<int:bookId>/<str:bookTitle>', create_review, name='create_review'),
    path('book/<int:bookId>/', book, name='book'),
    path('challengeList/', challengeList, name='challengeList'),
    path('challengePage/<int:object_id>', challengePage, name='challengePage'),
    path('apply/<int:challengeId>/', apply, name='apply'),
    path('bookRemove/<int:book_id>', bookRemove, name='bookRemove'),
    path('author_show_page/<int:idAuthor>', author_show_page, name='author_show_page'),
    path('author_clicked/<int:idAuthor>', author_clicked, name='author_clicked'),
    path('rate_book/<int:idBook>/', rate_book, name='rate_book'),
    path('add_reaction/', add_reaction, name='add_reaction'),
    path('addNewBook/', addNewBook, name='addNewBook'),
    path('addBookToDataBase/', addBookToDataBase, name='addBookToDataBase'),
    path('add_to_wishlist/<int:book_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('add_to_readlist/<int:book_id>/', add_to_readlist, name='add_to_readlist'),
    path('add_to_recommended/<int:book_id>/', add_to_recommended, name='add_to_recommended'),
    path('addNewChallenge/', addNewChallenge, name='addNewChallenge'),



    # Other URL patterns
]