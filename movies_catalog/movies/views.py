from django.shortcuts import render, redirect

from .models import Movie
from .forms import MovieForm

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden

from django.db.models import Q  # For complex lookups

def is_admin(user):
    return user.is_superuser or user.is_staff

# Create your views here.
def movies_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movies_list.html', {'movies': movies})

def movies_list_with_search(request):
# Get the search query from the GET parameters
    search_query = request.GET.get('q', '')  # 'q' is the query parameter
    movies = Movie.objects.all()

    if search_query:
        # Filter movies by title or actor name (case-insensitive search)
        movies = movies.filter(
            Q(title__icontains=search_query) |
            Q(actors__name__icontains=search_query)
        ).distinct()

    return render(request, 'movies/movies_list.html', {'movies': movies, 'search_query': search_query})
def movie_detail(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
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