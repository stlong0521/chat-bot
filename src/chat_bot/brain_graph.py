import simplejson as json
import operator
from utils import tokenize_exclude_punctuation

class BrainGraph:

    def __init__(self):
        self.graph = {}
        self.answer_word_cnt = {}

    def process_question_answer_pair(self, question, answer):
        question_word_list = tokenize_exclude_punctuation(question)
        answer_word_list = tokenize_exclude_punctuation(answer)
        for question_word in question_word_list:
            if question_word not in self.graph:
                self.graph[question_word] = {}
                self.graph[question_word]['word_cnt'] = 0
            question_word_cnt = self.graph[question_word]['word_cnt']
            for answer_word in [word for word in self.graph[question_word] if word != 'word_cnt']:
                self.graph[question_word][answer_word] *= 1.0 * question_word_cnt / (question_word_cnt + 1)
            for answer_word in answer_word_list:
                if answer_word in self.graph[question_word]:
                    self.graph[question_word][answer_word] = (self.graph[question_word][answer_word] * \
                                                             (question_word_cnt + 1) + 1) / \
                                                             (question_word_cnt + 1)
                else:
                    self.graph[question_word][answer_word] = 1.0 / (question_word_cnt + 1)
            self.graph[question_word]['word_cnt'] += 1
        # Count answer words
        for answer_word in answer_word_list:
            if answer_word in self.answer_word_cnt:
                self.answer_word_cnt[answer_word] += 1
            else:
                self.answer_word_cnt[answer_word] = 1

    def adjust_word_graph(self):
        for question_word in self.graph:
            for answer_word in self.graph[question_word]:
                if answer_word == 'word_cnt':
                    continue
                # self.graph[question_word][answer_word] /= self.answer_word_cnt[answer_word]
                # An answer word w_a could repeat in a sentence, but P(w_a|w_q) cannot exceed 1.0
                if self.graph[question_word][answer_word] > 1.0:
                    self.graph[question_word][answer_word] = 1.0

    def trim_word_graph(self, question_answer_pairs):
        trimmed_graph = {}
        for question, answer in question_answer_pairs:
            relevant_edges = {}
            question_word_list = tokenize_exclude_punctuation(question)
            answer_word_list = tokenize_exclude_punctuation(answer)
            for question_word in question_word_list:
                for answer_word in answer_word_list:
                    # The score is confidence of answer_word given question_word over support of answer_word from all answers
                    relevant_edges[(question_word, answer_word)] = self.graph[question_word][answer_word] / \
                                                                   (1.0 * self.answer_word_cnt[answer_word] / len(question_answer_pairs))
            sorted_edges = sorted(relevant_edges.items(), key=operator.itemgetter(1), reverse=True)
            for edge, score in sorted_edges:
                if not question_word_list and not answer_word_list:
                    break
                question_word, answer_word = edge
                # Skip if both question_word and answer_word have been connected by other edges
                if question_word not in question_word_list and answer_word not in answer_word_list:
                    continue
                # Skip if connection confidence is less than appearance of answer word by chance
                if score < 1.0:
                    continue
                # Skip if the connection pattern appears only once
#                if self.graph[question_word][answer_word] * self.graph[question_word]['word_cnt'] < 2:
#                    continue
                if question_word not in trimmed_graph:
                    trimmed_graph[question_word] = {}
                trimmed_graph[question_word][answer_word] = score
                question_word_list = [word for word in question_word_list if word != question_word]
                answer_word_list = [word for word in answer_word_list if word != answer_word]
        self.graph = trimmed_graph

    def find_potential_answer_words(self, question):
        answer_word_dict = {}
        question_word_list = tokenize_exclude_punctuation(question)
        len_question_word_list = len(question_word_list)
        for question_word in [word for word in question_word_list if word in self.graph]:
            for answer_word in [word for word in self.graph[question_word] if word != 'word_cnt']:
                if answer_word in answer_word_dict:
                    answer_word_dict[answer_word] += self.graph[question_word][answer_word]
                else:
                    answer_word_dict[answer_word] = self.graph[question_word][answer_word]
        return {k: v / len_question_word_list for k, v in answer_word_dict.items()}
