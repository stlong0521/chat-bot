import pytest
from brain_graph import BrainGraph
from copy import deepcopy

@pytest.fixture
def brain_graph():
    graph = BrainGraph()
    graph.load_graph_from_json("test/data/brain_graph.json")
    return graph

class TestBrainGraph:

    def test_load_graph_from_json(self, brain_graph):
        assert brain_graph.graph["How"]["fine"] == 2
        assert brain_graph.graph["How"]["good"] == 1
        assert brain_graph.graph["are"]["am"] == 4
        assert brain_graph.graph["are"]["be"] == 3
        assert brain_graph.graph["you"]["I"] == 6
        assert brain_graph.graph["you"]["you"] == 5
        assert brain_graph.graph["?"]["."] == 8
        assert brain_graph.graph["?"]["!"] == 7

    def test_write_graph_to_json(self, brain_graph):
        # Sanity test
        graph = deepcopy(brain_graph.graph)
        brain_graph.write_graph_to_json("test/data/brain_graph.json")
        brain_graph.load_graph_from_json("test/data/brain_graph.json")
        assert brain_graph.graph == graph

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
        assert brain_graph.graph["?"]["."] == 9
        assert brain_graph.graph["How"]["I"] == 1
        assert brain_graph.graph["How"]["am"] == 1
        assert brain_graph.graph["How"]["."] == 1
        assert brain_graph.graph["are"]["I"] == 1
        assert brain_graph.graph["are"]["fine"] == 1
        assert brain_graph.graph["are"]["."] == 1
        assert brain_graph.graph["you"]["am"] == 1
        assert brain_graph.graph["you"]["fine"] == 1
        assert brain_graph.graph["you"]["."] == 1
        assert brain_graph.graph["?"]["I"] == 1
        assert brain_graph.graph["?"]["am"] == 1
        assert brain_graph.graph["?"]["fine"] == 1

    def test_retrieve_most_related_word(self, brain_graph):
        assert brain_graph.retrieve_most_related_word("When") == None
        assert brain_graph.retrieve_most_related_word("How") == "fine"
        assert brain_graph.retrieve_most_related_word("are") == "am"
        assert brain_graph.retrieve_most_related_word("you") == "I"
        assert brain_graph.retrieve_most_related_word("?") == "."

    def test_retrieve_answer_of_question(self, brain_graph):
        question = "How are you?"
        expected_answer_word_list = ["fine", "am", "I", "."]
        assert brain_graph.retrieve_answer_of_question(question) == expected_answer_word_list
