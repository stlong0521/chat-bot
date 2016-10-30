import pytest
from copy import deepcopy
from brain_graph import BrainGraph
from utils import load_dict_from_file

@pytest.fixture
def brain_graph():
    graph = BrainGraph()
    graph.graph = load_dict_from_file("test/data/brain_graph.json")
    return graph

class TestBrainGraph:

    def test_process_question_answer_pair(self, brain_graph):
        graph = deepcopy(brain_graph.graph)
        question = "How are you doing?"
        answer = "I am fine."
        brain_graph.process_question_answer_pair(question, answer)
        assert brain_graph.graph["how"]["word_cnt"] == graph["how"]["word_cnt"] + 1
        assert brain_graph.graph["how"]["i"] == 1.0 / (graph["how"]["word_cnt"] + 1)
        assert brain_graph.graph["how"]["am"] == 1.0 / (graph["how"]["word_cnt"] + 1)
        assert brain_graph.graph["how"]["fine"] == (graph["how"]["fine"] * \
                                                   graph["how"]["word_cnt"] + 1) / \
                                                   (graph["how"]["word_cnt"] + 1)
        assert brain_graph.graph["are"]["word_cnt"] == graph["are"]["word_cnt"] + 1
        assert brain_graph.graph["are"]["i"] == 1.0 / (graph["are"]["word_cnt"] + 1)
        assert brain_graph.graph["are"]["am"] == (graph["are"]["am"] * \
                                                 graph["are"]["word_cnt"] + 1) / \
                                                 (graph["are"]["word_cnt"] + 1)
        assert brain_graph.graph["are"]["fine"] == 1.0 / (graph["are"]["word_cnt"] + 1)
        assert brain_graph.graph["you"]["word_cnt"] == graph["you"]["word_cnt"] + 1
        assert brain_graph.graph["you"]["i"] == (graph["you"]["i"] * \
                                                graph["you"]["word_cnt"] + 1) / \
                                                (graph["you"]["word_cnt"] + 1)
        assert brain_graph.graph["you"]["am"] == 1.0 / (graph["you"]["word_cnt"] + 1)
        assert brain_graph.graph["you"]["fine"] == 1.0 / (graph["you"]["word_cnt"] + 1)
        assert brain_graph.graph["doing"]["word_cnt"] == 1
        assert brain_graph.graph["doing"]["i"] == 1.0
        assert brain_graph.graph["doing"]["am"] == 1.0
        assert brain_graph.graph["doing"]["fine"] == 1.0

    def test_find_potential_answer_words(self, brain_graph):
        brain_graph.graph["how"]["i"] = 0.1
        question = "How are you doing?"
        expected_answer_word_dict = {"i": 1.0 - (1.0 - 0.8) * (1.0 - 0.1), "you": 0.5,
                                     "am": 0.7, "be": 0.4, "fine": 0.7, "good": 0.9}
        assert brain_graph.find_potential_answer_words(question) == expected_answer_word_dict
