import simplejson as json
import random
import string
import math

from utils import tokenize, untokenize

class SentenceTrie:

    def __init__(self):
        self.trie = {}

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

    def build_trie_from_sentences(self, sentences):
        for sentence in sentences:
            self.add_sentence_to_trie(sentence)

    def ask_a_question(self):
        question_word_list = []
        curr_trie = self.trie
        while curr_trie:
            word = random.choice(curr_trie.keys())
            if word == 'sen_cnt':
                break
            else:
                question_word_list.append(word)
                curr_trie = curr_trie[word]
        return untokenize(question_word_list)

    def reconstruct_sentence(self, answer_word_dict):
        curr_node = self.trie
        curr_answer_word_list = []
        curr_score = 0.0
        curr_answer_candidate = []
        curr_answer_candidate_score = [0]
        self._search_sentence_trie(answer_word_dict,
                                   curr_node,
                                   curr_answer_word_list,
                                   curr_score,
                                   curr_answer_candidate,
                                   curr_answer_candidate_score)
        return untokenize(curr_answer_candidate)

    def _search_sentence_trie(self,
                              answer_word_dict,
                              curr_node,
                              curr_answer_word_list,
                              curr_score,
                              curr_answer_candidate,
                              curr_answer_candidate_score):
        for word in curr_node:
            if word == "sen_cnt":
                len_exclude_punctuation = len([word for word in curr_answer_word_list if word not in string.punctuation])
                len_penalty = math.sqrt(len_exclude_punctuation)
                if curr_score / len_penalty > curr_answer_candidate_score[0]:
                    curr_answer_candidate_score[0] = curr_score / len_penalty
                    del curr_answer_candidate[:]
                    curr_answer_candidate.extend(curr_answer_word_list)
            else:
                curr_answer_word_list.append(word)
                self._search_sentence_trie(answer_word_dict,
                                           curr_node[word],
                                           curr_answer_word_list,
                                           curr_score + answer_word_dict.get(word.lower(), 0.0),
                                           curr_answer_candidate,
                                           curr_answer_candidate_score)
                curr_answer_word_list.pop()
