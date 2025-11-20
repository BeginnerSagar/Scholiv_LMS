from storages.backends.s3boto3 import S3Boto3Storage

class PublicMediaStorage(S3Boto3Storage):
    """
    Custom storage backend that forces public-read ACL on all uploads.
    """
    location = ''  # No prefix
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False