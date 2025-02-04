import os

# 设置 Django 的 settings 模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tracer.settings")  # 请根据实际项目路径修改
import django

django.setup()

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


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
