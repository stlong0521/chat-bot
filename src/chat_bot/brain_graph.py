import simplejson as json
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
                self.graph[question_word][answer_word] /= self.answer_word_cnt[answer_word]
                # An answer word w_a could repeat in a sentence, but P(w_a|w_q) cannot exceed 1.0
                if self.graph[question_word][answer_word] > 1.0:
                    self.graph[question_word][answer_word] = 1.0

    def find_potential_answer_words(self, question):
        answer_word_dict = {}
        question_word_list = tokenize_exclude_punctuation(question)
        for question_word in [word for word in question_word_list if word in self.graph]:
            for answer_word in [word for word in self.graph[question_word] if word != 'word_cnt']:
                if answer_word in answer_word_dict:
                    answer_word_dict[answer_word] *= (1.0 - self.graph[question_word][answer_word])
                else:
                    answer_word_dict[answer_word] = 1.0 - self.graph[question_word][answer_word]
        return {k: 1.0 - v for k, v in answer_word_dict.items()}
