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
        brain_graph.add_cell_edge("How", "fine")
        # Add a non-existing edge with a non-existing ending cell
        brain_graph.add_cell_edge("How", "OK")
        # Add a non-existing edge with a non-existing starting cell
        brain_graph.add_cell_edge("What", "good")
        # Add a non-existing edge with non-existing starting and ending cells
        brain_graph.add_cell_edge("Why", "because")
        # Assertion
        assert brain_graph.graph["How"]["fine"] == 3
        assert brain_graph.graph["How"]["OK"] == 1
        assert brain_graph.graph["What"]["good"] == 1
        assert brain_graph.graph["Why"]["because"] == 1

    def test_process_question_answer_pair(self, brain_graph):
        question = "How are you?"
        answer = "I am fine."
        brain_graph.process_question_answer_pair(question, answer)
        assert brain_graph.graph["How"]["fine"] == 3
        assert brain_graph.graph["are"]["am"] == 5
        assert brain_graph.graph["you"]["I"] == 7
        assert brain_graph.graph["How"]["I"] == 1
        assert brain_graph.graph["How"]["am"] == 1
        assert brain_graph.graph["are"]["I"] == 1
        assert brain_graph.graph["are"]["fine"] == 1
        assert brain_graph.graph["you"]["am"] == 1
        assert brain_graph.graph["you"]["fine"] == 1

    def test_retrieve_most_related_word(self, brain_graph):
        assert brain_graph.retrieve_most_related_word("When") == None
        assert brain_graph.retrieve_most_related_word("How") == "fine"
        assert brain_graph.retrieve_most_related_word("are") == "am"
        assert brain_graph.retrieve_most_related_word("you") == "I"

    def test_retrieve_answer_of_question(self, brain_graph):
        question = "How are you?"
        expected_answer_word_list = ["fine", "am", "I"]
        assert brain_graph.retrieve_answer_of_question(question) == expected_answer_word_list

    def test_find_potential_answer_words(self, brain_graph):
        brain_graph.add_cell_edge("How", "I")
        question = "How are you doing?"
        expected_answer_word_dict = {"I": 7, "you": 5, "am": 4, "be": 3, "fine": 2, "good": 1}
        assert brain_graph.find_potential_answer_words(question) == expected_answer_word_dict
