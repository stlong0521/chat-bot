import simplejson as json
from utils import tokenize

class SentenceTrie:

    def __init__(self):
        self.trie = {}

    def load_trie_from_json(self, json_file_path):
        with open(json_file_path) as json_file:
            self.trie = json.load(json_file)

    def write_trie_to_json(self, json_file_path):
        with open(json_file_path, "w") as json_file:
            json.dump(self.trie, json_file)

    def add_sentence_to_trie(self, sentence):
        word_list = tokenize(sentence)
        curr_node = self.trie
        for word in word_list:
            if word not in curr_node:
                curr_node[word] = {}
            curr_node = curr_node[word]
        if "sen_cnt" in curr_node:
            curr_node["sen_cnt"] = curr_node["sen_cnt"] + 1
        else:
            curr_node["sen_cnt"] = 1

    def reconstruct_sentence(self, word_list):
        pass
