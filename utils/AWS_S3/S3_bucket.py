import os

# 设置 Django 的 settings 模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tracer.settings")  # 请根据实际项目路径修改
import django

django.setup()

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from urllib.parse import urlparse


def create_s3_bucket(bucket_name):
    """
    创建一个 S3 桶，桶名称必须全局唯一
    """
    region = settings.AWS_DEFAULT_REGION
    client_params = {
        'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
        'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
    }

    # 如果区域是 us-east-1，则使用全局端点（防止请求被发送到区域性端点导致错误）
    if region == 'us-east-1':
        client_params['region_name'] = region
        client_params['endpoint_url'] = 'https://s3.amazonaws.com'
    else:
        client_params['region_name'] = region

    s3_client = boto3.client('s3', **client_params)

    try:
        if region == 'us-east-1':
            # us-east-1 区域创建桶时不要指定 CreateBucketConfiguration
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        print(f"Error creating bucket: {e}")






def upload_file_to_s3(bucket_name, file_obj, object_name=None):
    if object_name is None:
        object_name = file_obj.name

    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    try:
        # 移除 ACL 参数
        s3_client.upload_fileobj(file_obj, bucket_name, object_name)
        print(f"File '{object_name}' uploaded successfully to bucket '{bucket_name}'.")

        region = settings.AWS_DEFAULT_REGION
        if region == 'us-east-1':
            file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        else:
            file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_name}"

        return file_url
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return None







def delete_file_from_s3(bucket_name, object_key):
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        # 可选：打印返回的 response 以供调试
        print("Delete response:", response)
    except ClientError as e:
        print(f"Error deleting file from S3: {e}")
        return False
    return True







def delete_file_list_from_s3(bucket_name, key_list):
    if not key_list:
        print("没有要删除的文件")
        return True

    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    # 构造 Delete 参数，Delete 参数需要包含一个 "Objects" 列表，
    # 列表中的每个字典至少包含 "Key" 键
    delete_params = {
        'Objects': [{'Key': key} for key in key_list],
        'Quiet': False  # 可选，若设置为 True，则删除响应中不会返回被删除的对象信息
    }

    try:
        response = s3_client.delete_objects(Bucket=bucket_name, Delete=delete_params)
        print("Delete response:", response)
    except ClientError as e:
        print(f"Error deleting files from S3: {e}")
        return False
    return True





def get_temporary_credentials(duration_seconds=3600):
    sts_client = boto3.client(
        'sts',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )
    try:
        response = sts_client.get_session_token(DurationSeconds=duration_seconds)
        credentials = response['Credentials']
        return credentials
    except ClientError as e:
        print("Error obtaining temporary credentials:", e)
        return None



