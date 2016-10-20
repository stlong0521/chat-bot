from copy import deepcopy
from brain_graph import BrainGraph
from sentence_trie import SentenceTrie
from utils import (load_dict_from_s3, write_dict_to_s3, delete_file_in_s3,
                   load_item_from_dynamo, write_item_to_dynamo)

class ChatBot:

    def __init__(self):
        self.mode = 'talking'
        self.graph = BrainGraph()
        self.trie = SentenceTrie()
        self.new_question_answer_pairs = []
        self.brain_version = ('', '')
        self.sync_memory()

    def __del__(self):
        while not self.sync_memory(): pass

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
            self.new_question_answer_pairs.append((self.most_recent_question, sentence))
            self.learn(self.most_recent_question, sentence)
            response = 'Thanks! New information learned!'
        elif sentence.lower() == 'sync memory':
            if self.sync_memory():
                response = 'Memory synced!'
            else:
                response = 'Someone else is syncing! You may want to try again later!'
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

    def sync_memory(self):
        # Back up the current brain in case sync memory fails
        brain_graph = deepcopy(self.graph.graph)
        sentence_trie = deepcopy(self.trie.trie)
        # If the remote brain has a diverged version, FETCH
        latest_brain_version = load_item_from_dynamo()
        if latest_brain_version != self.brain_version:
            self.graph.graph = load_dict_from_s3('brain_graph.json', version=latest_brain_version[0])
            self.trie.trie = load_dict_from_s3('sentence_trie.json', version=latest_brain_version[1])
        # If the bot does not have any new knowledge, no need for MERGE or PUSH
        if not self.new_question_answer_pairs:
            self.brain_version = latest_brain_version
            return True
        # If the remote brain has a diverged version, MERGE
        if latest_brain_version != self.brain_version:
            for question, answer in self.new_question_answer_pairs:
                self.learn(question, answer)
        # Then, PUSH
        updated_brain_version = (write_dict_to_s3('brain_graph.json', self.graph.graph),
                                 write_dict_to_s3('sentence_trie.json', self.trie.trie))
        if not write_item_to_dynamo(updated_brain_version, latest_brain_version):
            # PUSH failed, recover the backup brain and delete the brain files just uploaded
            self.graph.graph = brain_graph
            self.trie.trie = sentence_trie
            delete_file_in_s3('brain_graph.json', updated_brain_version[0])
            delete_file_in_s3('sentence_trie.json', updated_brain_version[1])
            return False
        else:
            # PUSH succeeded, update the brain version and delete the out-of-date brain files
            self.brain_version = updated_brain_version
            self.new_question_answer_pairs = []
            delete_file_in_s3('brain_graph.json', latest_brain_version[0])
            delete_file_in_s3('sentence_trie.json', latest_brain_version[1])
            return True
