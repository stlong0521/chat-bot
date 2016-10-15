import os.path
from brain_graph import BrainGraph
from sentence_trie import SentenceTrie
from utils import load_dict_from_s3, write_dict_to_s3

class ChatBot:

    def __init__(self):
        self.mode = 'talking'
        self.graph = BrainGraph()
        self.graph.graph = load_dict_from_s3('brain_graph.json')
        self.trie = SentenceTrie()
        self.trie.trie = load_dict_from_s3('sentence_trie.json')

    def interact(self):
        while True:
            sentence = raw_input('Question/Command/Expected Answer: ')
            response = self.respond(sentence)
            if isinstance(response, tuple):
                for r in response:
                    print 'Response:', r
            else:
                print 'Response:', response

    def respond(self, sentence):
        if self.mode == 'learning' and self.waiting_for_answer:
            self.waiting_for_answer = False
            self.learn(self.most_recent_question, sentence)
            response = 'Thanks! New information learned!'
        elif sentence.lower() == 'bye' or sentence.lower() == 'goodbye':
            write_dict_to_s3('brain_graph.json', self.graph.graph)
            write_dict_to_s3('sentence_trie.json', self.trie.trie)
            response = 'Bye!'
        elif sentence.lower() == 'switch to learning':
            self.mode = 'learning'
            self.waiting_for_answer = False
            response = 'Switched to learning!'
        elif sentence.lower() == 'switch to talking':
            self.mode = 'talking'
            response = 'Switched to talking!'
        else:
            self.most_recent_question = sentence
            answer_word_dict = self.graph.find_potential_answer_words(sentence)
            answer = self.trie.reconstruct_sentence(answer_word_dict)
            response = answer if answer else 'I am not mature enough to answer this question.'
            if self.mode == 'learning' and not self.waiting_for_answer:
                response = (response, 'I am learning. Please tell me your expected answer.')
                self.waiting_for_answer = True
        return response

    def learn(self, question, answer):
        self.graph.process_question_answer_pair(question, answer)
        self.trie.add_sentence_to_trie(answer)
