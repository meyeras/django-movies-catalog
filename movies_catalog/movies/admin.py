from django.contrib import admin

from .models import Movie, Actor
# Register your models here.
from django.contrib import admin
from .models import Movie, Actor

class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'year_of_release', 'director', 'get_actors', 'poster']
    filter_horizontal = ['actors']

    # Reference the existing get_actors method from the Movie model
    def get_actors(self, obj):
        # Call the get_actors method defined in the Movie model
        actors = obj.get_actors()
        return "; ".join([actor.name for actor in actors])  # Display actors' names in a semicolon-separated format

    get_actors.short_description = 'Actors'

admin.site.register(Movie)
#admin.site.register(Movie, MovieAdmin)
admin.site.register(Actor)
