# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_stream, put_data, put_file
from Liusgram import app
from flask import request
import os
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = app.config['QINIU_ACCESS_KEY']
secret_key = app.config['QINIU_SECRET_KEY']
#构建鉴权对象
q = Auth(access_key, secret_key)
#要上传的空间
bucket_name = app.config['QBUCKET']
domain_prefix = app.config['QDOMAIN']


###################################################
#### not support the upload by stream function
####
###################################################
def upload_file_from_stream(file_name, file):
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, file_name)
    print file.stream
    ret, info = put_stream(token, file_name, file.stream, file.stream.tell(), check_crc = False)

    print type(info.status_code), info
    if info.status_code == 200:
        return domain_prefix + file_name
    return None
def upload_file_from_path(save_file_name, source_file):
    token = q.upload_token(bucket_name, save_file_name)
    ret, info = put_file(token, save_file_name, source_file)
    print type(info.status_code), info
    if info.status_code == 200:
        return domain_prefix + save_file_name
    return None

if __name__ == '__main__':
    upload_file_from_path('test1.jpg', 'test1.jpg')