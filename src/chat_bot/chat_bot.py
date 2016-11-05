from copy import deepcopy
from brain_graph import BrainGraph
from sentence_trie import SentenceTrie
from utils import (load_dict_from_s3, write_dict_to_s3, delete_file_in_s3,
                   load_item_from_dynamo, write_item_to_dynamo)

class ChatBot:

    def __init__(self):
        self.mode = 'talking'
        self.word_graph = BrainGraph()
        self.answer_trie = SentenceTrie()
        self.new_question_answer_pairs = []
        self.brain_version = ('', '')
        self.sync_memory()
        self.question_trie = SentenceTrie()
        self.question_trie.trie = load_dict_from_s3(
                                      'ts-chat-bot',
                                      'question_trie.json'
                                  )

    def interact(self):
        while True:
            sentence = raw_input('You: ')
            response = self.respond(sentence)
            if isinstance(response, tuple):
                for r in response:
                    print 'Bot:', r
            else:
                print 'Bot:', response

    def respond(self, sentence):
        if sentence.lower() == 'sync memory':
            if self.sync_memory():
                response = 'Memory synced with the remote brain!'
            else:
                response = 'Someone else is syncing! You may want to try again later!'
        elif sentence.lower() == 'switch to talking':
            self.mode = 'talking'
            response = 'Switched to talking'
        elif sentence.lower() == 'switch to learning':
            self.mode = 'learning'
            response = 'Switched to learning'
            self.most_recent_question = self.question_trie.ask_a_question()
            response = (response, self.most_recent_question)
        else:
            if self.mode == 'talking':
                response = self.answer(sentence)
            else:
                self.new_question_answer_pairs.append((self.most_recent_question, sentence))
                self.learn(self.most_recent_question, sentence)
                self.most_recent_question = self.question_trie.ask_a_question()
                response = 'Thanks! Your feedback was recorded!'
                response = (response, self.most_recent_question)
        return response

    def answer(self, question):
        answer_word_dict = self.word_graph.find_potential_answer_words(question)
        answer = self.answer_trie.reconstruct_sentence(answer_word_dict)
        return answer if answer else 'I am not mature enough to answer this question.'

    def learn(self, question, answer):
        self.word_graph.process_question_answer_pair(question, answer)
        self.answer_trie.add_sentence_to_trie(answer)

    def sync_memory(self):
        # Back up the current brain in case sync memory fails
        word_graph = deepcopy(self.word_graph.graph)
        answer_trie = deepcopy(self.answer_trie.trie)
        # If the remote brain has a diverged version, FETCH
        latest_brain_version = load_item_from_dynamo()
        if latest_brain_version != self.brain_version:
            self.word_graph.graph = load_dict_from_s3('ts-chat-bot',
                                                      'brains/word_graph.json',
                                                      version=latest_brain_version[0])
            self.answer_trie.trie = load_dict_from_s3('ts-chat-bot',
                                                      'brains/answer_trie.json',
                                                      version=latest_brain_version[1])
        # If the bot does not have any new knowledge, no need for MERGE or PUSH
        if not self.new_question_answer_pairs:
            self.brain_version = latest_brain_version
            return True
        # If the remote brain has a diverged version, MERGE
        if latest_brain_version != self.brain_version:
            for question, answer in self.new_question_answer_pairs:
                self.learn(question, answer)
        # Then, PUSH
        updated_brain_version = (write_dict_to_s3('ts-chat-bot',
                                                  'brains/word_graph.json',
                                                  self.word_graph.graph),
                                 write_dict_to_s3('ts-chat-bot',
                                                  'brains/answer_trie.json',
                                                  self.answer_trie.trie))
        if not write_item_to_dynamo(updated_brain_version, latest_brain_version):
            # PUSH failed, recover the backup brain and delete the brain files just uploaded
            self.word_graph.graph = word_graph
            self.answer_trie.trie = answer_trie
            delete_file_in_s3('ts-chat-bot',
                              'brains/word_graph.json',
                              updated_brain_version[0])
            delete_file_in_s3('ts-chat-bot',
                              'brains/answer_trie.json',
                              updated_brain_version[1])
            return False
        else:
            # PUSH succeeded, update the brain version and delete the out-of-date brain files
            self.brain_version = updated_brain_version
            self.new_question_answer_pairs = []
            delete_file_in_s3('ts-chat-bot',
                              'brains/word_graph.json',
                              latest_brain_version[0])
            delete_file_in_s3('ts-chat-bot',
                              'brains/answer_trie.json',
                              latest_brain_version[1])
            return True
