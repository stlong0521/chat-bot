import simplejson as json
import random

from utils import tokenize

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
        return " ".join(question_word_list)

    def reconstruct_sentence(self, answer_word_dict):
        curr_node = self.trie
        curr_answer_word_list = []
        curr_score = 1.0
        curr_answer_candidate = []
        curr_answer_candidate_score = [0]
        self._search_sentence_trie(answer_word_dict,
                                   curr_node,
                                   curr_answer_word_list,
                                   curr_score,
                                   curr_answer_candidate,
                                   curr_answer_candidate_score)
        return " ".join(curr_answer_candidate)

    def _search_sentence_trie(self,
                              answer_word_dict,
                              curr_node,
                              curr_answer_word_list,
                              curr_score,
                              curr_answer_candidate,
                              curr_answer_candidate_score):
        for word in curr_node:
            if word == "sen_cnt":
                if 1.0 - curr_score > curr_answer_candidate_score[0]:
                    curr_answer_candidate_score[0] = 1.0 - curr_score
                    del curr_answer_candidate[:]
                    curr_answer_candidate.extend(curr_answer_word_list)
            else:
                curr_answer_word_list.append(word)
                self._search_sentence_trie(answer_word_dict,
                                           curr_node[word],
                                           curr_answer_word_list,
                                           # An epsilon is introduced here to distinguish 0.0 and 0.0 * 0.0
                                           curr_score * (1.0 - answer_word_dict.get(word.lower(), 0) + 1e-2),
                                           curr_answer_candidate,
                                           curr_answer_candidate_score)
                curr_answer_word_list.pop()
