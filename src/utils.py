from __future__ import division
from nltk import word_tokenize
import string
import simplejson as json

def tokenize(sentence):
    return word_tokenize(sentence)

def tokenize_exclude_punctuation(sentence):
    word_list = []
    for word in tokenize(sentence):
        if word not in string.punctuation:
            word_list.append(word)
    return word_list

def load_dict_from_file(json_file_path):
    with open(json_file_path) as json_file:
        return json.load(json_file)

def write_dict_to_file(json_file_path, dictionary):
    with open(json_file_path, "w") as json_file:
        json.dump(dictionary, json_file)
