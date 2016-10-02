import simplejson as json
from utils import tokenize

class BrainGraph:

    def __init__(self):
        self.graph = {}

    def load_graph_from_json(self, json_file_path):
        with open(json_file_path) as json_file:
            self.graph = json.load(json_file)

    def write_graph_to_json(self, json_file_path):
        with open(json_file_path, "w") as json_file:
            json.dump(self.graph, json_file)

    def add_cell_edge(self, word_in_question, word_in_answer):
        if word_in_question in self.graph:
            if word_in_answer in self.graph[word_in_question]:
                self.graph[word_in_question][word_in_answer] = self.graph[word_in_question][word_in_answer] + 1
            else:
                self.graph[word_in_question][word_in_answer] = 1
        else:
            self.graph[word_in_question] = {}
            self.graph[word_in_question][word_in_answer] = 1

    def process_question_answer_pair(self, question, answer):
        question_word_list = tokenize(question)
        answer_word_list = tokenize(answer)
        for question_word in question_word_list:
            for answer_word in answer_word_list:
                self.add_cell_edge(question_word, answer_word)

    def retrieve_most_related_word(self, word):
        if word not in self.graph:
            return None
        return max(self.graph[word], key=(lambda key: self.graph[word][key]))

    def retrieve_answer_of_question(self, question):
        answer_word_list = []
        question_word_list = tokenize(question)
        for question_word in question_word_list:
            answer_word = self.retrieve_most_related_word(question_word)
            if answer_word:
                answer_word_list.append(answer_word)
        return answer_word_list
