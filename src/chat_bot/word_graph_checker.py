import operator
import re
from brain_graph import BrainGraph
from utils import load_item_from_dynamo, load_dict_from_s3

class WordGraphChecker:

    def __init__(self):
        self.word_graph = BrainGraph()
        latest_brain_version = load_item_from_dynamo()
        self.word_graph.graph = load_dict_from_s3('ts-chat-bot',
                                                  'brains/word_graph.json',
                                                  version=latest_brain_version[0])

    def check_word_graph(self):
        while True:
            word_and_cnt = raw_input('Input (word, top x): ')
            conn = self.get_conn(tuple(re.split(', *', word_and_cnt)))
            print conn

    def get_conn(self, args):
        word = args[0]
        if word not in self.word_graph.graph:
            return 'Word does not exist!'
        if(len(args) > 1):
            cnt = int(args[1])
        else:
            cnt = len(self.word_graph.graph[word])
        unsorted_conn = self.word_graph.graph[word]
        conn = sorted(unsorted_conn.items(), key=operator.itemgetter(1), reverse=True)[:cnt]
        return '\n'.join(map(lambda x: str(x), conn))
