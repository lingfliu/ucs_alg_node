from minio import Minio
from minio.error import S3Error
class MinioCli:
    """
    Minio cli
    """
    def __init__(self, host, port, bucket, username, passwd):
        self.host = host
        self.port = port
        self.bucket = bucket # by default only one bucket
        self.username = username
        self.passwd = passwd

        try:
            self.cli = Minio(host+':'+str(port), access_key=username, secret_key=passwd, secure=False)
            found = self.cli.bucket_exists(bucket)
            if not found:
                self.cli.make_bucket(bucket)

        except S3Error as e:
            print(e)
            self.cli = None

    def upload(self, obj_name, obj_path):
        """上传文件，io操作，建议线程操作"""
        if not self.cli:
            return -1
        try:
            self.cli.fput_object(self.bucket, obj_name, obj_path)
            return 0
        except S3Error as e:
            print(e)
            return -1

    def download(self, obj_name, obj_path):
        """直接下载文件，io操作，建议线程操作"""
        if not self.cli:
            return -1
        try:
            self.cli.fget_object(self.bucket, obj_name, obj_path)
            return 0
        except S3Error as e:
            print(e)
            return -1

    def bucket_exist(self, bucket):
        if self.cli.bucket_exists(bucket):
            return True
        else:
            return False

    def create_bucket(self, bucket):
        try:
            self.cli.make_bucket(bucket)
            return 0
        except S3Error as e:
            print(e)
            return -1

    def query(self, obj_name):
        if not self.cli:
            return -1
        try:
            return self.cli.stat_object(self.bucket, obj_name)
        except S3Error as e:
            print(e)
            return -1

    def fetch_share_url(self, obj_name):
        """Fetch a shareable url for the object"""
        if not self.cli:
            return -1
        try:
            return self.cli.presigned_get_object(self.bucket, obj_name)
        except S3Error as e:
            print(e)
            return -1

    def query_all(self):
        if not self.cli:
            return -1
        try:
            return self.cli.list_objects(self.bucket)
        except S3Error as e:
            print(e)
            return -1

    def count(self):
        """
        Count the number of objects in the bucket
        """
        if not self.cli:
            return -1
        try:
            return len([c for c in self.cli.list_objects(self.bucket)])
        except S3Error as e:
            print(e)
            return -1



