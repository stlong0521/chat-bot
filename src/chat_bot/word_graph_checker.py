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
            cli_input = raw_input('Input (question word, top x | answer word): ')
            print self.get_conn(tuple(re.split(', *', cli_input)))

    def get_conn(self, args):
        question_word = args[0]
        if question_word not in self.word_graph.graph:
            return 'Question word does not exist!'
        if len(args) > 1 and not re.compile("^[\d]+$").match(args[1]):
            answer_word = args[1]
            return self.word_graph.graph[question_word].get(answer_word)
        if len(args) == 1:
            cnt = len(self.word_graph.graph[question_word])
        else:
            cnt = int(args[1])
        unsorted_conn = self.word_graph.graph[question_word]
        conn = sorted(unsorted_conn.items(), key=operator.itemgetter(1), reverse=True)[:cnt]
        return '\n'.join(map(lambda x: str(x), conn))
