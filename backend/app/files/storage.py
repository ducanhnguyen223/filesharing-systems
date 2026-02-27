import boto3
from botocore.exceptions import ClientError
from functools import lru_cache
from app.core.config import get_settings


class StorageClient:
    def __init__(self, settings=None):
        if settings is None:
            settings = get_settings()
        self._client = boto3.client(
            "s3",
            region_name=settings.SPACES_REGION,
            endpoint_url=settings.SPACES_ENDPOINT,
            aws_access_key_id=settings.SPACES_KEY,
            aws_secret_access_key=settings.SPACES_SECRET,
        )
        self._bucket = settings.SPACES_BUCKET
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def upload_file(self, file_obj, key: str, content_type: str = "application/octet-stream") -> str:
        self._client.upload_fileobj(
            file_obj,
            self._bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return key

    def download_file(self, key: str):
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"]

    def delete_file(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires,
        )


@lru_cache
def get_storage_client() -> StorageClient:
    return StorageClient()
