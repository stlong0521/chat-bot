import os

from brain_graph import BrainGraph
from sentence_trie import SentenceTrie
from utils import (load_dict_from_file, write_dict_to_s3, delete_file_in_s3,
                   load_item_from_dynamo, write_item_to_dynamo, write_dict_to_file)
from chat_bot import ChatBot

class ChatBotTrainer:

    def __init__(self):
        self.word_graph = BrainGraph()
        self.answer_trie = SentenceTrie()
        self.question_answer_pairs = []

    def learn_and_validate(self):
        for dirpath, dirnames, filenames in os.walk("data/english-conversations/smalltalk"):
            for filename in filenames:
                conversation = load_dict_from_file(os.path.join(dirpath, filename))
                self.learn_from_conversation(conversation)
        self.word_graph.adjust_word_graph()
        self.word_graph.trim_word_graph(self.question_answer_pairs)
        self.sync_memory()
        # For test
        write_dict_to_file("data/word_graph.json", self.word_graph.graph)
        write_dict_to_file("data/answer_trie.json", self.answer_trie.trie)
        print "Response accuracy: {}".format(self.calc_response_accuracy())

    # Learn from easy conversations
    def learn_from_conversation(self, conversation):
        prev = ""
        for curr in conversation:
            if prev != "Scene divider" and curr != "Scene divider":
                self.word_graph.process_question_answer_pair(prev, curr)
                self.answer_trie.add_sentence_to_trie(curr)
                self.question_answer_pairs.append((prev, curr))
            prev = curr

    # Validate the model
    def calc_response_accuracy(self):
        test_chat_bot = ChatBot()
        cnt = 0
        for question, answer in self.question_answer_pairs:
            response = test_chat_bot.answer(question)
            if response == answer:
                cnt += 1
            else:
                print "Question: {}".format(question)
                print "Answer: {}".format(response)
                print "Expected: {}".format(answer)
        return 1.0 * cnt / len(self.question_answer_pairs)

    # Learn from episode lines
    def learn_from_lines(self, conversation):
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
