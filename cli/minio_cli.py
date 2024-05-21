from minio import Minio
from minio.error import S3Error
class MinioCli:
    def __init__(self, host, port, bucket, username, passwd):
        self.host = host
        self.port = port
        self.bucket = bucket
        self.username = username
        self.passwd = passwd

        try:
            self.cli = Minio(host+':'+port, access_key=username, secret_key=passwd)
            found = self.cli.bucket_exists(bucket)
        except S3Error as e:
            print(e)
            self.cli = None

    def upload(self, obj_name, obj_path):
        if not self.cli:
            return -1
        try:
            self.cli.fput_object(self.bucket, obj_name, obj_path)
            return 0
        except S3Error as e:
            print(e)
            return -1

    def download(self, obj_name, obj_path):
        if not self.cli:
            return -1
        try:
            self.cli.fget_object(self.bucket, obj_name, obj_path)
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

    def query_all(self):
        if not self.cli:
            return -1
        try:
            return self.cli.list_objects(self.bucket)
        except S3Error as e:
            print(e)
            return -1

    def count(self):
        if not self.cli:
            return -1
        try:
            return len(self.cli.list_objects(self.bucket))
        except S3Error as e:
            print(e)
            return -1



