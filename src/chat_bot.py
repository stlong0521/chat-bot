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
            sentence = raw_input('Question/Command: ').lower()
            if sentence == 'bye' or sentence == 'goodbye':
                write_dict_to_s3('brain_graph.json', self.graph.graph)
                write_dict_to_s3('sentence_trie.json', self.trie.trie)
                print 'Response: Bye!'
                break
            if sentence == 'switch to training':
                self.mode = 'training'
                print 'Response: Switched to training mode!'
                continue
            if sentence == 'switch to talking':
                self.mode = 'talking'
                print 'Response: Switched to talking mode!'
                continue
            answer_word_dict = self.graph.find_potential_answer_words(sentence)
            response = self.trie.reconstruct_sentence(answer_word_dict)
            response = response if response else 'I am not mature enough to answer this question.'
            print 'Response:', response
            if self.mode == 'training':
                expected_response = raw_input('Expected response: ')
                self.graph.process_question_answer_pair(sentence, expected_response)
                self.trie.add_sentence_to_trie(expected_response)
