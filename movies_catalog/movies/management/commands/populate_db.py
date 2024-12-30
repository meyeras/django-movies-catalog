import json
import asyncio
import aiofiles
import os
from aiohttp import ClientSession, ClientError
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Actor


# Asynchronous function to check if the URL points to a valid image
async def download_image_url(movie, session: ClientSession, semaphore, posters_folder) -> dict:
    url = movie["poster"]
    os.makedirs(posters_folder, exist_ok=True)
    file_name = url.split("/")[-1]
    destination_path = os.path.join(posters_folder, file_name)

    if os.path.exists(destination_path):
        print(f"The image '{destination_path}' already exists.")
        movie['poster_status'] = 'Valid'
        return movie
    try:
        async with semaphore:  # Use semaphore to limit concurrency
            print(f"Download poster url: {url} for movie {movie["title"]}")
            # Send an asynchronous GET request
            async with session.get(url, timeout=10) as response:
                # Check if the request was successful
                if response.status == 200:
                    # Open the file in binary write mode asynchronously
                    async with aiofiles.open(destination_path, "wb") as file:
                        # Write the response content to the file
                        await file.write(await response.read())
                        print(f"Image downloaded and saved as '{destination_path}'")
                        movie["poster_status"] = "Valid"
                        print(f"Check poster url: {url} for movie {movie["title"]} IS VALID")

                else:
                    print(f"Failed to download image. HTTP Status: {response.status}")
                    movie["poster_status"] = "Invalid"
                    print(f"Check poster url: {url} for movie {movie["title"]} IS INVALID")

    except (ClientError, asyncio.TimeoutError):
        movie["poster_status"] = "Invalid"
        print(f"Check poster url: {url} for movie {movie["title"]} IS INVALID")

    return movie  # Return the updated movie object



async def filter_movies_with_invalid_poster_url(movies):
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent requests
    posters_folder = settings.MEDIA_ROOT + "/posters"
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


def populate_movies(movies):
    # Populate the database
    created_count = 0
    for entry in movies:
        try:
            movie, created = Movie.objects.get_or_create(
                title=entry['title'],
                year_of_release=entry['year'],
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
        json_file = kwargs['json_file']

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

        # Call the asynchronous method using asyncio.run
        filtered_movies = asyncio.run(filter_movies_with_invalid_poster_url(data))

        #Populate the database with the filtered movies
        populate_movies(filtered_movies)
