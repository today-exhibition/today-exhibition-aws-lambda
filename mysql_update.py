import boto3
import os
import json
import pymysql

from config import RDS_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORTDB 

s3_client = boto3.client('s3')

# RDS 연결 정보 설정
rds_host = RDS_HOST
db_name = DB_NAME
db_user = DB_USER
db_password = DB_PASSWORD
db_port = DB_PORTDB

# RDS 연결
def connect_to_rds():
    connection = pymysql.connect(
            host=rds_host,
            user=db_user,
            password=db_password,
            db=db_name,
            port=db_port,
            cursorclass=pymysql.cursors.DictCursor
        )
    return connection

def lambda_handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name'] 
        object_key = record['s3']['object']['key'] 
        
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        exhibition_id = (object_key.split('/')[1]).split('.')[0]
        
        # low_thumbnail_img 갱신
        connection = connect_to_rds()
        if connection:
            with connection.cursor() as cursor:
                sql = "UPDATE exhibition SET low_thumbnail_img = %s WHERE id = %s"
                cursor.execute(sql, (image_url, exhibition_id))
                connection.commit()
        connection.close()