import os
import shutil

import boto3
from django.core.management.base import BaseCommand
from movies.models import Movie, Actor
from django.conf import settings
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage

class Command(BaseCommand):
    help = "Cleanup the Movies catalog by deleting all movies, actors, and poster files."

    def delete_S3_files_with_prefix(self, prefix):
        """
        Deletes all files in the S3 bucket that start with the given prefix.

        :param prefix: The prefix to match (e.g., "uploads/temp/")
        """
        if isinstance(default_storage, S3Boto3Storage):
            # ✅ Get the S3 client and bucket name
            s3_client = boto3.client("s3")
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # ✅ List all objects with the given prefix
            objects_to_delete = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            if "Contents" in objects_to_delete:
                delete_keys = [{"Key": obj["Key"]} for obj in objects_to_delete["Contents"]]

                # ✅ Perform batch delete
                s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": delete_keys})

                print(f"✅ Deleted {len(delete_keys)} files from S3 with prefix '{prefix}'")
            else:
                print(f"⚠️ No files found with prefix '{prefix}'")
        else:
            print("❌ default_storage is using local storage, not S3")

    def handle(self, *args, **kwargs):
        # Delete all movies
        movies_deleted, _ = Movie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {movies_deleted} movies."))

        # Delete all actors
        actors_deleted, _ = Actor.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {actors_deleted} actors."))

        # Cleanup posters folder
        if isinstance(default_storage, S3Boto3Storage): # if the posters are in S3
            self.delete_S3_files_with_prefix("posters/")
        else:
            posters_path = os.path.join(settings.MEDIA_ROOT, 'posters')
            if os.path.exists(posters_path):
                shutil.rmtree(posters_path)  # Remove the directory and all its contents
                os.makedirs(posters_path)  # Recreate an empty posters directory
                self.stdout.write(self.style.SUCCESS("Cleaned up the 'posters' folder."))
            else:
                self.stdout.write(self.style.WARNING("The 'posters' folder does not exist."))
