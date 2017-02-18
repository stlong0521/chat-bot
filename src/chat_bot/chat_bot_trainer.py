import os

from brain_graph import BrainGraph
from sentence_trie import SentenceTrie
from utils import (load_dict_from_file, write_dict_to_s3, delete_file_in_s3,
                   load_item_from_dynamo, write_item_to_dynamo, write_dict_to_file)

class ChatBotTrainer:

    def __init__(self):
        self.word_graph = BrainGraph()
        self.answer_trie = SentenceTrie()

    def learn(self):
        for dirpath, dirnames, filenames in os.walk("data/friends-scripts"):
            for filename in filenames:
                conversation = load_dict_from_file(os.path.join(dirpath, filename))
                self.learn_from_conversation(conversation)
        # Clean the word graph by keeping only patterns that have repeated
        for conn in self.word_graph.graph.values():
            word_cnt = conn["word_cnt"]
            for key, value in conn.items():
                if conn[key] * word_cnt < 2 and key != "word_cnt":
                    del conn[key]
        self.word_graph.adjust_word_graph()
        self.sync_memory()
        # For test
        write_dict_to_file("data/word_graph.json", self.word_graph.graph)
        write_dict_to_file("data/answer_trie.json", self.answer_trie.trie)

    def learn_from_conversation(self, conversation):
        prev_role = ""
        prev_line = ""
        for curr in conversation:
            curr_role = curr.keys()[0]
            curr_line = curr.values()[0]
            if curr_role.lower() == "ross" and \
                prev_role.lower() != "dummy" and prev_role.lower() != "ross":
                self.word_graph.process_question_answer_pair(prev_line, curr_line)
                self.answer_trie.add_sentence_to_trie(curr_line)
            prev_role = curr_role
            prev_line = curr_line

    def sync_memory(self):
        """
        Different from ChatBot, memory sync here will replace the brain in S3 entirely
        """
        latest_brain_version = load_item_from_dynamo()
        updated_brain_version = (write_dict_to_s3('ts-chat-bot',
                                                  'brains/word_graph.json',
                                                  self.word_graph.graph),
                                 write_dict_to_s3('ts-chat-bot',
                                                  'brains/answer_trie.json',
                                                  self.answer_trie.trie))
        write_item_to_dynamo(updated_brain_version, latest_brain_version)
        delete_file_in_s3('ts-chat-bot',
                          'brains/word_graph.json',
                          latest_brain_version[0])
        delete_file_in_s3('ts-chat-bot',
                          'brains/answer_trie.json',
                          latest_brain_version[1])
