# file_uploader.py MinIO Python SDK example
from minio import Minio
from minio.error import S3Error

def main():
    # Create a client with the MinIO server playground, its access key 使用MinI0服务器游乐场及其访问密钥创建客户端
    # and secret key.
    client = Minio(
    # endpoint指定的是你Minio的远程IP及端口
    #     endpoint="127.0.0.1:9090",
        "localhost:9090",
        access_key="admin",
        secret_key="admin1234",
        # 建议为False
        secure=False
    )

    # The file to upload, change this path if needed 本地文件上传
    source_file = r"D:\py program\ucs_alg_node\requirements.txt"

    # The destination bucket and filename on the MinIO server 保存在public下的requirements.txt
    bucket_name = "pubilc"
    destination_file = "requirements04.txt"

    # Make the bucket if it doesn't exist.判断是否存在bucket_name
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name, destination_file, source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
