from django.urls import path
from .views import movies_list, register_movie, movie_detail, movies_list_with_search
from .views import MovieAPIView, MovieDetailAPIView

urlpatterns = [
    path('', movies_list, name='movies_list'),
    path('movies-list/', movies_list_with_search, name='movies-list'),
    path('register-movie/', register_movie, name='register-movie'),
    path('movie-detail/<int:movie_id>/', movie_detail, name='movie-detail'),

    path('api/movies/', MovieAPIView.as_view(), name='movies-list-api'),
    path('api/movies/<int:movie_id>/', MovieDetailAPIView.as_view(), name='movie-detail-api'),
]