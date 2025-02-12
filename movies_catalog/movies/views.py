from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from .models import Movie
from .forms import MovieForm

from django.contrib.auth.decorators import user_passes_test

from django.db.models import Q  # For complex lookups
from .serializers import MovieSerializer


def get_movies(request, search_query=None):
    movies = Movie.objects.all()

    if search_query:
        # Filter movies by title or actor name (case-insensitive search)
        movies = movies.filter(
            Q(title__icontains=search_query) |
            Q(actors__name__icontains=search_query)
        ).distinct()
    return movies

def get_movie_detail(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return movie

def is_admin(user):
    return user.is_superuser or user.is_staff

# Create your views here.
def movies_list(request):
    movies = get_movies(request)
    return render(request, 'movies/movies_list.html', {'movies': movies})

def movies_list_with_search(request):
    # Get the search query from the GET parameters
    search_query = request.GET.get('q', '')  # 'q' is the query parameter
    movies = get_movies(request, search_query)
    return render(request, 'movies/movies_list.html', {'movies': movies, 'search_query': search_query})

def movie_detail(request, movie_id):
    movie = get_movie_detail(request, movie_id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})

@user_passes_test(is_admin)
def register_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save()
            return redirect('movie-detail', movie_id=movie.id)
        else:
            print(form.errors)
    else:
        form = MovieForm()
        return render(request, 'movies/register_movie.html',{'form': form} )


class MovieAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Enable multipart support
    def get_permissions(self):
        """Custom permission handling:
        - GET requests: Public access
        - POST requests: Admins only
        """
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]  # Only admins can create movies
        return [permissions.IsAuthenticated()]  # Public access for GET

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                description="Search movies by title or actor",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: MovieSerializer(many=True)},
        security=[{'Bearer': []}]
    )

    def get(self, request, movie_id=None, *args, **kwargs):
        """Get movie list (public)"""
        movies = get_movies(request)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Register a new movie",
        request_body=MovieSerializer,
        consumes=['multipart/form-data'],
        responses={201: "Movie created successfully"},
        security=[{'Bearer': []}]
    )

    def post(self, request, *args, **kwargs):
        """Register a new movie (Admin Only)"""
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MovieDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [permissions.IsAdminUser()]  # Only admins can create movies
        return [permissions.IsAuthenticated()]  # Public access for GET

    """Retrieve a specific movie by its ID"""
    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, id=movie_id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    """Delete a specific movie by its ID (Admin only)"""
    def delete(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, id=movie_id)

        # Check if movie has an associated poster and delete it
        if movie.poster:
            try:
                # Get the file path of the poster
                poster_path = movie.poster.name  # Use 'name' when using cloud storage like S3
                # Delete the file from storage (cloud or local)
                if default_storage.exists(poster_path):
                    default_storage.delete(poster_path)
            except Exception as e:
                return Response({"detail": f"Failed to delete poster: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Delete the movie
        movie.delete()
        return Response({"detail": "Movie deleted successfully."}, status=status.HTTP_204_NO_CONTENT)