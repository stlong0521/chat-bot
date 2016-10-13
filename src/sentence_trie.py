import simplejson as json
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

    def reconstruct_sentence(self, answer_word_dict):
        curr_node = self.trie
        curr_answer_word_list = []
        curr_score = 0
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
                if curr_score > curr_answer_candidate_score[0]:
                    curr_answer_candidate_score[0] = curr_score
                    del curr_answer_candidate[:]
                    curr_answer_candidate.extend(curr_answer_word_list)
            else:
                curr_answer_word_list.append(word)
                self._search_sentence_trie(answer_word_dict,
                                           curr_node[word],
                                           curr_answer_word_list,
                                           curr_score + answer_word_dict.get(word.lower(), 0),
                                           curr_answer_candidate,
                                           curr_answer_candidate_score)
                curr_answer_word_list.remove(word)
