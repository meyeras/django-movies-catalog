import json
import asyncio
import traceback

import aiofiles
import os
from aiohttp import ClientSession, ClientError
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Actor

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# import posixpath


# Asynchronous function to check if the URL points to a valid image
async def download_image_url(movie, session: ClientSession, semaphore, posters_folder) -> dict:
    url = movie["poster"]
    image_name = url.split("/")[-1]
    file_path = f"{posters_folder}/{image_name}"  # Relative path for storage

    # ✅ Check if the file already exists
    # TODO: check why the following code always return False for the exists method
    # if await asyncio.to_thread(default_storage.exists, file_path):
    #     print(f"⚠️ Skipping {image_name} - already exists in storage")
    #     movie['poster_status'] = 'Valid'
    #     return movie

    try:
        default_storage.open(file_path)
        print(f"⚠️ Skipping {image_name} - already exists in storage")
        movie['poster_status'] = 'Valid'
        return movie
    except Exception as e:
        # File doesn't exist
        print(f"{file_path} does not exist, proceed to download")

    try:
        async with semaphore:  # Use semaphore to limit concurrency
            print(f"Download poster url: {url} for movie {movie["title"]}")
            # Send an asynchronous GET request
            async with session.get(url, timeout=20) as response:
                # Check if the request was successful
                if response.status == 200:
                    # Read the binary content
                    image_data = await response.read()

                    #SYNCHRONOUSLY save the image to the destination path
                    #TODO: wrap this function in some async context
                    default_storage.save(file_path, ContentFile(image_data))

                    movie["poster_status"] = "Valid"
                    print(f"✅ Image saved at: {file_path}")
                else:
                    print(f"Failed to download image. HTTP Status: {response.status}")
                    movie["poster_status"] = "Invalid"
                    print(f"Check poster url: {url} for movie {movie["title"]} IS INVALID")

    except (ClientError, asyncio.TimeoutError) as error:
        movie["poster_status"] = "Invalid"
        print(f"Check poster url: {image_name} for movie {movie["title"]} IS INVALID, error: {error}")

    return movie  # Return the updated movie object


async def filter_movies_with_invalid_poster_url(movies):
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent requests
    posters_folder = "posters"
    async with ClientSession() as session:
        # Use asyncio.gather to run multiple tasks concurrently
        tasks = [download_image_url(movie, session, semaphore, posters_folder) for movie in movies]
        movies_with_poster_status = await asyncio.gather(*tasks)


    filtered_movies = [movie for movie in movies_with_poster_status if
                       movie.get("poster_status") == "Valid"]
    for movie in filtered_movies:
        movie['poster'] = 'posters/' + movie['poster'].split("/")[-1]
        del movie['poster_status']
    return filtered_movies

def batch_populate_movies(movies_data):
    # Step 1: Fetch only relevant movies (Correctly combining title & year_of_release)
    movie_identifiers = [(entry["title"], entry["year_of_release"]) for entry in movies_data]

    # Fetch only movies matching any title OR any year
    candidate_movies = Movie.objects.filter(
        title__in=[m[0] for m in movie_identifiers],
        year_of_release__in=[m[1] for m in movie_identifiers]
    )

    # Now filter in Python to ensure (title, year) match correctly
    existing_movies = {
        (m.title, m.year_of_release): m
        for m in candidate_movies
        if (m.title, m.year_of_release) in movie_identifiers
    }

    # Step 2: Fetch only relevant actors
    actor_names = {name for entry in movies_data for name in entry["cast"]}
    existing_actors = {a.name: a for a in Actor.objects.filter(name__in=actor_names)}

    movies_to_create = []
    actors_to_create = set()
    movie_actor_links = []

    # Step 3: Prepare movies & actors for bulk insert
    for entry in movies_data:
        movie_key = (entry["title"], entry["year_of_release"])

        if movie_key not in existing_movies:  # If movie doesn't exist
            movie = Movie(
                title=entry["title"],
                year_of_release=entry["year_of_release"],
                description=entry["description"],
                poster=entry["poster"],
                director=entry["director"]
            )
            movies_to_create.append(movie)

        # Collect actor names to avoid duplicate queries
        if entry["cast"]:
            for name in entry["cast"]:
                if name not in existing_actors:
                    actors_to_create.add(name)

    # Step 4: Bulk create movies (but they don't have IDs yet!)
    movies_count = Movie.objects.count()
    Movie.objects.bulk_create(movies_to_create, ignore_conflicts=True)
    movies_created_count = Movie.objects.count() - movies_count

    # Step 5: Fetch newly inserted movies to get their IDs (Correct Filtering)
    candidate_movies = Movie.objects.filter(
        title__in=[m.title for m in movies_to_create],
        year_of_release__in=[m.year_of_release for m in movies_to_create]
    )

    # Now filter in Python to ensure (title, year) match correctly
    existing_movies.update({
        (m.title, m.year_of_release): m
        for m in candidate_movies
        if (m.title, m.year_of_release) in movie_identifiers
    })

    # Step 6: Bulk create actors (avoiding duplicates)
    actors_to_create = [Actor(name=name) for name in actors_to_create]
    actors_count = Actor.objects.count()
    Actor.objects.bulk_create(actors_to_create, ignore_conflicts=True)
    actors_created_count = Actor.objects.count() - actors_count

    # Refresh existing actors with newly created ones
    existing_actors.update({a.name: a for a in Actor.objects.filter(name__in=actor_names)})

    # Step 7: Prepare many-to-many relationships (now with correct IDs)
    for entry in movies_data:
        movie = existing_movies[(entry["title"], entry["year_of_release"])]

        if entry["cast"]:
            for name in entry["cast"]:
                actor = existing_actors[name]
                movie_actor_links.append(movie.actors.through(movie_id=movie.id, actor_id=actor.id))

    # Step 8: Bulk insert movie-actor relationships
    Movie.actors.through.objects.bulk_create(movie_actor_links, ignore_conflicts=True)

    print(f"{movies_created_count} new movies added, {actors_created_count} actors added")


def populate_movies(movies):
    # Populate the database
    created_count = 0
    for entry in movies:
        try:
            movie, created = Movie.objects.get_or_create(
                title=entry['title'],
                year_of_release=entry['year_of_release'],
                description=entry['description'],
                poster=entry['poster'],
                director=entry['director']
            )
            if created:
                created_count += 1
                if entry['cast']:
                    for name in entry['cast']:
                        actor, created = Actor.objects.get_or_create(name=name)
                        if actor:
                            movie.actors.add(actor)

        except KeyError as e:
            print(f"Skipping entry due to missing field: {e}")

    print(f"Successfully added {created_count} movies to the database.")


class Command(BaseCommand):
    help = "Populates the Movie database with data from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='The path to the JSON file containing movie data.'
        )

    def handle(self, *args, **kwargs):
        json_file = kwargs.get('json_file') or 'movies_sample.json'

        # Load the JSON file
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stderr.write(f"Error: File '{json_file}' not found.")
            return
        except json.JSONDecodeError:
            self.stderr.write(f"Error: File '{json_file}' is not valid JSON.")
            return


        from storages.backends.s3boto3 import S3Boto3Storage

        if isinstance(default_storage, S3Boto3Storage):
            print("✅ Using S3 Storage")
        else:
            print("✅ Using Local FileSystem Storage")

        # Call the asynchronous method using asyncio.run
        filtered_movies = asyncio.run(filter_movies_with_invalid_poster_url(data))
        print(f"Total filtered movies: {len(filtered_movies)}")

        #Populate the database with the filtered movies

        # num_duplicates = 10  # Adjust to test different dataset sizes
        # movies_data = filtered_movies * num_duplicates  # Multiply list
        # import random
        # random.shuffle(movies_data)  # Shuffle the list
        # batch_populate_movies(movies_data)

        batch_populate_movies(filtered_movies)
