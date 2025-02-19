from django.core.files.storage import default_storage
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging
from functools import lru_cache


@lru_cache()
def get_s3_client():
    """
    Lazily create and cache S3 client using Django settings

    Returns:
        boto3.client: Configured S3 client
    """
    return boto3.client('s3')
    # kwargs = {}
    #
    # # Only add credentials if they're configured
    # if hasattr(settings, 'AWS_ACCESS_KEY_ID'):
    #     kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
    # if hasattr(settings, 'AWS_SECRET_ACCESS_KEY'):
    #     kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY
    # if hasattr(settings, 'AWS_S3_REGION_NAME'):
    #     kwargs['region_name'] = settings.AWS_S3_REGION_NAME
    #
    # return boto3.client('s3', **kwargs)


def get_bucket_name():
    """
    Get bucket name from settings with fallback to storage backend

    Returns:
        str: S3 bucket name
    """
    if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
        return settings.AWS_STORAGE_BUCKET_NAME

    # Fallback to getting bucket name from storage backend
    storage = default_storage
    if hasattr(storage, 'bucket_name'):
        return storage.bucket_name
    if hasattr(storage, 'bucket'):
        return storage.bucket

    raise ValueError(
        "Could not determine S3 bucket name. Please configure AWS_STORAGE_BUCKET_NAME or use a storage backend that provides bucket information.")


def debug_s3_file_access(file_path):
    """
    Debug utility to compare direct S3 access vs Django's default_storage
    for a given file path.

    Args:
        file_path (str): The file path to check

    Returns:
        dict: Results of various checks
    """
    results = {
        'file_path': file_path,
        'default_storage_exists': False,
        's3_direct_exists': False,
        'normalized_path': None,
        'full_s3_path': None,
        'error': None
    }

    try:
        # Check using default_storage first
        results['default_storage_exists'] = default_storage.exists(file_path)

        # Get S3 client
        s3 = get_s3_client()
        bucket_name = get_bucket_name()

        # Normalize the path (remove leading slash if present)
        normalized_path = file_path.lstrip('/')
        results['normalized_path'] = normalized_path

        # Construct full S3 path
        full_s3_path = f"{settings.AWS_LOCATION}/{normalized_path}" if hasattr(settings,
                                                                               'AWS_LOCATION') else normalized_path
        results['full_s3_path'] = full_s3_path

        # Check directly with S3
        try:
            s3.head_object(Bucket=bucket_name, Key=full_s3_path)
            results['s3_direct_exists'] = True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                results['s3_direct_exists'] = False
            else:
                raise

    except Exception as e:
        results['error'] = str(e)
        logging.error(f"Error checking S3 file: {str(e)}")

    return results


def list_bucket_contents(prefix=None):
    """
    List all objects in the S3 bucket with an optional prefix filter

    Args:
        prefix (str, optional): Filter results to objects starting with this prefix

    Returns:
        list: List of object keys in the bucket
    """
    try:
        s3 = get_s3_client()
        bucket_name = get_bucket_name()

        kwargs = {
            'Bucket': bucket_name
        }
        if prefix:
            kwargs['Prefix'] = prefix

        response = s3.list_objects_v2(**kwargs)
        return [obj['Key'] for obj in response.get('Contents', [])]

    except Exception as e:
        logging.error(f"Error listing bucket contents: {str(e)}")
        return []

