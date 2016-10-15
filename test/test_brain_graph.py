import pytest
from brain_graph import BrainGraph
from utils import load_dict_from_file

@pytest.fixture
def brain_graph():
    graph = BrainGraph()
    graph.graph = load_dict_from_file("test/data/brain_graph.json")
    return graph

class TestBrainGraph:

    def test_add_cell_edge(self, brain_graph):
        # Add to an existing edge
        brain_graph.add_cell_edge("how", "fine")
        # Add a non-existing edge with a non-existing ending cell
        brain_graph.add_cell_edge("how", "OK")
        # Add a non-existing edge with a non-existing starting cell
        brain_graph.add_cell_edge("what", "good")
        # Add a non-existing edge with non-existing starting and ending cells
        brain_graph.add_cell_edge("why", "because")
        # Assertion
        assert brain_graph.graph["how"]["fine"] == 3
        assert brain_graph.graph["how"]["OK"] == 1
        assert brain_graph.graph["what"]["good"] == 1
        assert brain_graph.graph["why"]["because"] == 1

    def test_process_question_answer_pair(self, brain_graph):
        question = "How are you?"
        answer = "I am fine."
        brain_graph.process_question_answer_pair(question, answer)
        assert brain_graph.graph["how"]["fine"] == 3
        assert brain_graph.graph["are"]["am"] == 5
        assert brain_graph.graph["you"]["i"] == 7
        assert brain_graph.graph["how"]["i"] == 1
        assert brain_graph.graph["how"]["am"] == 1
        assert brain_graph.graph["are"]["i"] == 1
        assert brain_graph.graph["are"]["fine"] == 1
        assert brain_graph.graph["you"]["am"] == 1
        assert brain_graph.graph["you"]["fine"] == 1

    def test_retrieve_most_related_word(self, brain_graph):
        assert brain_graph.retrieve_most_related_word("when") == None
        assert brain_graph.retrieve_most_related_word("how") == "fine"
        assert brain_graph.retrieve_most_related_word("are") == "am"
        assert brain_graph.retrieve_most_related_word("you") == "i"

    def test_retrieve_answer_of_question(self, brain_graph):
        question = "How are you?"
        expected_answer_word_list = ["fine", "am", "i"]
        assert brain_graph.retrieve_answer_of_question(question) == expected_answer_word_list

    def test_find_potential_answer_words(self, brain_graph):
        brain_graph.add_cell_edge("how", "i")
        question = "How are you doing?"
        expected_answer_word_dict = {"i": 7, "you": 5, "am": 4, "be": 3, "fine": 2, "good": 1}
        assert brain_graph.find_potential_answer_words(question) == expected_answer_word_dict
