from __future__ import division
from nltk import word_tokenize
import string
import simplejson as json
import boto3, botocore
import os

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
    s3_client.download_file('ts-chat-bot', 'brains/' + file_name, 'data/' + file_name)
    return load_dict_from_file('data/' + file_name)

def write_dict_to_s3(file_name, dictionary):
    write_dict_to_file('data/' + file_name, dictionary)
    s3_client = boto3.client('s3')
    s3_client.upload_file('data/' + file_name, 'ts-chat-bot', 'brains/' + file_name)
