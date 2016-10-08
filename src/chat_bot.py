import os.path
from brain_graph import BrainGraph
from sentence_trie import SentenceTrie
from utils import load_dict_from_file, write_dict_to_file

class ChatBot:

    def __init__(self):
        self.mode = 'talking'
        self.graph = BrainGraph()
        if os.path.isfile('data/brain_graph.json'):
            self.graph.graph = load_dict_from_file('data/brain_graph.json')
        self.trie = SentenceTrie()
        if os.path.isfile('data/sentence_trie.json'):
            self.trie.trie = load_dict_from_file('data/sentence_trie.json')

    def interact(self):
        while True:
            sentence = raw_input('Question/Command: ')
            if sentence.lower() == 'we are done':
                write_dict_to_file('data/brain_graph.json', self.graph.graph)
                write_dict_to_file('data/sentence_trie.json', self.trie.trie)
                print 'Response: Bye!'
                break
            elif sentence.lower() == 'switch to training':
                self.mode = 'training'
                print 'Response: Switched to training mode!'
                continue
            elif sentence.lower() == 'switch to talking':
                self.mode = 'talking'
                print 'Response: Switched to talking mode!'
                continue
            answer_word_dict = self.graph.find_potential_answer_words(sentence)
            print 'Response:', self.trie.reconstruct_sentence(answer_word_dict)
            if self.mode == 'training':
                expected_response = raw_input('Expected response: ')
                self.graph.process_question_answer_pair(sentence, expected_response)
                self.trie.add_sentence_to_trie(expected_response)
