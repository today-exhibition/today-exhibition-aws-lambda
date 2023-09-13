import boto3
from urllib.parse import unquote_plus
from PIL import Image

s3_client = boto3.client('s3')

def reduce_image_quality(image_path, reduced_path, content_type):
    with Image.open(image_path) as image:
        # 이미지 품질 설정 (0부터 100까지의 값, 높을수록 높은 화질)
        quality = 50 

        # 이미지를 다시 저장하면서 화질 설정 적용
        image.save(reduced_path, format=content_type.split('/')[-1], quality=quality)

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        # 폴더 경로에서 파일 이름 추출
        file_name = key.split('/')[-1]
    
        download_path = '/tmp/{}'.format(file_name)
        upload_key_low_quality = 'low_quality_imgs/{}'.format(file_name)
        
        # 다운로드 후 저화질 처리
        s3_client.download_file(bucket, key, download_path)
        response = s3_client.head_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        reduce_image_quality(download_path, download_path, content_type)
        
        s3_client.upload_file(download_path, bucket, upload_key_low_quality, ExtraArgs={'ContentType': content_type})