import boto3


class ObjectStorageBase:

    def __init__(self, endpoint_url, access_key, secret_key, bucket):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        try:
            self.s3.create_bucket(Bucket=self.bucket)
        except Exception:
            pass

    def check_file(self, key):
        try:
            obj = self.s3.head_object(Bucket=self.bucket, Key=key)
            return obj
        except Exception:
            return

    def get_link_file(self, key):
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': key
            },
            ExpiresIn=3600*24  # set expiration time for 24 hour
        )
        return url
