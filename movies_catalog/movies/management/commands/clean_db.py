import os
import shutil
from django.core.management.base import BaseCommand
from movies.models import Movie, Actor
from django.conf import settings

class Command(BaseCommand):
    help = "Cleanup the Movies catalog by deleting all movies, actors, and poster files."

    def handle(self, *args, **kwargs):
        # Delete all movies
        movies_deleted, _ = Movie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {movies_deleted} movies."))

        # Delete all actors
        actors_deleted, _ = Actor.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {actors_deleted} actors."))

        # Cleanup posters folder
        posters_path = os.path.join(settings.MEDIA_ROOT, 'posters')
        if os.path.exists(posters_path):
            shutil.rmtree(posters_path)  # Remove the directory and all its contents
            os.makedirs(posters_path)  # Recreate an empty posters directory
            self.stdout.write(self.style.SUCCESS("Cleaned up the 'posters' folder."))
        else:
            self.stdout.write(self.style.WARNING("The 'posters' folder does not exist."))
