from __future__ import division
from nltk import word_tokenize
import string
import simplejson as json
import boto3, botocore
import os
import requests
from datetime import datetime

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

def load_dict_from_s3(file_name, version=None):
    s3_client = boto3.client('s3')
    params={'Bucket': 'ts-chat-bot', 'Key': 'brains/' + file_name}
    if version:
        params['VersionId'] = version
    url = s3_client.generate_presigned_url('get_object', 
                                           Params=params, 
                                           ExpiresIn=30)
    return json.loads(requests.get(url).text)

def write_dict_to_s3(file_name, dictionary):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('put_object', 
                                           Params={'Bucket': 'ts-chat-bot',
                                                   'Key': 'brains/' + file_name}, 
                                           ExpiresIn=30)
    response = requests.put(url, data=json.dumps(dictionary))
    return response.headers['x-amz-version-id']

def delete_file_in_s3(file_name, version):
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket='ts-chat-bot',
                            Key='brains/' + file_name,
                            VersionId=version)

def load_item_from_dynamo():
    dynamo_client = boto3.client('dynamodb')
    response = dynamo_client.get_item(TableName='brain-version',
                                      Key={'Tag': {'S': 'latest'}},
                                      ProjectionExpression='BrainGraphVersion, SentenceTrieVersion')
    return response['Item']['BrainGraphVersion']['S'], response['Item']['SentenceTrieVersion']['S']

def write_item_to_dynamo(updated_brain_version, old_brain_version):
    dynamo_client = boto3.client('dynamodb')
    item = {'Tag': {'S': 'latest'},
            'BrainGraphVersion': {'S': updated_brain_version[0]},
            'SentenceTrieVersion': {'S': updated_brain_version[1]},
            'UpdatedTime': {'S': str(datetime.now())}
           }
    condition_expression = 'BrainGraphVersion = :bgv and SentenceTrieVersion = :stv'
    expression_attribute_values = {':bgv': {'S': old_brain_version[0]},
                                   ':stv': {'S': old_brain_version[1]}}
    response = dynamo_client.put_item(TableName='brain-version',
                                      Item=item,
                                      ConditionExpression=condition_expression,
                                      ExpressionAttributeValues=expression_attribute_values)
    return response['ResponseMetadata']['HTTPStatusCode'] == 200
