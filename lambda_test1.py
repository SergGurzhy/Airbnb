
import boto3
import os
import requests

URLS = [
    r'https://a0.muscache.com/im/pictures/miso/Hosting-726845935107239384/original/6fa853f5-dd7f-4e15-87f1-ba836bb25ee8.jpeg?im_w=1440',
    r'https://a0.muscache.com/im/pictures/miso/Hosting-726845935107239384/original/dc9c4454-64b3-411b-875d-1776ce9f056e.jpeg?im_w=1440',
    r'https://a0.muscache.com/im/pictures/miso/Hosting-726845935107239384/original/3b1d3c69-e081-45d2-95d1-2abc5f836e05.jpeg?im_w=1440',
    r'https://a0.muscache.com/im/pictures/miso/Hosting-726845935107239384/original/e40c90b8-d875-49f2-98a6-bec9cf199482.jpeg?im_w=1440',
    r'https://a0.muscache.com/im/pictures/miso/Hosting-726845935107239384/original/7e4bf23b-8579-404a-8fe1-735e20c9dfc0.jpeg?im_w=1440',
]

FOLDER_NAME = 'bnbbucket-test'
AWS_DEFAULT_REGION = "us-east-1"
os.environ['AWS_DEFAULT_REGION'] = AWS_DEFAULT_REGION


def _s3_worker(folder_name: str, file_name: str, data: bytes | dict) -> None:
    bucket_name = os.environ['BUCKET'].lower()
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=f"{folder_name}/{file_name}", Body=data, ContentType='application/json')


def download_and_save_img() -> str:
    for index in range(len(URLS)):
        file_name = URLS[index]
        data = requests.get(URLS[index]).content
        _s3_worker(folder_name=FOLDER_NAME, file_name=file_name, data=data)

    return f"downloading: {len(URLS)} files"

