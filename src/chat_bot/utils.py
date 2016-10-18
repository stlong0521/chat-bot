from __future__ import division
from nltk import word_tokenize
import string
import simplejson as json
import boto3, botocore
import os
import requests

def tokenize(sentence):
    return word_tokenize(sentence)

def tokenize_exclude_punctuation(sentence):
    word_list = []
    for word in tokenize(sentence.lower()):
        if word not in string.punctuation:
            word_list.append(word)
    return word_list

def load_dict_from_file(json_file_path):
    with open(json_file_path) as json_file:
        return json.load(json_file)

def write_dict_to_file(json_file_path, dictionary):
    with open(json_file_path, "w") as json_file:
        json.dump(dictionary, json_file)

def load_dict_from_s3(file_name):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('get_object', 
                                           Params={'Bucket': 'ts-chat-bot',
                                                   'Key': 'brains/' + file_name}, 
                                           ExpiresIn=30)
    return json.loads(requests.get(url).text)

def write_dict_to_s3(file_name, dictionary):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('put_object', 
                                           Params={'Bucket': 'ts-chat-bot',
                                                   'Key': 'brains/' + file_name}, 
                                           ExpiresIn=30)
    requests.put(url, data=json.dumps(dictionary))
