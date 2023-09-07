import boto3
from urllib.parse import unquote_plus
from PIL import Image

s3_client = boto3.client('s3')

def reduce_image_quality(image_path, reduced_path, content_type):
    with Image.open(image_path) as image:
        # 이미지 품질 설정 (0부터 100까지의 값, 높을수록 높은 화질)
        quality = 50 
        # 이미지를 JPEG로 다시 저장하면서 화질 설정 적용
        image.save(reduced_path, format=content_type.split('/')[-1], quality=quality)

def lambda_handler(event):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        tmpkey = key.replace('/', '')
        
        # 다운로드 경로 설정
        download_path = '/tmp/{}'.format(tmpkey)
        # 업로드 경로 설정
        upload_bucket = '{}-low-resolution'.format(bucket)
        upload_path = '/tmp/resized-{}'.format(tmpkey)
        
        s3_client.download_file(bucket, key, download_path)

        # 업로드된 파일의 메타데이터 가져오기
        response = s3_client.head_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        
        reduce_image_quality(download_path, upload_path, content_type)
        # 화질이 낮아진 이미지 S3에 업로드 (메타데이터 포함)
        s3_client.upload_file(upload_path, upload_bucket, key, ExtraArgs={'ContentType': content_type})

