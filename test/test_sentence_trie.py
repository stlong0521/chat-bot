import pytest
from sentence_trie import SentenceTrie
from copy import deepcopy

@pytest.fixture
def sentence_trie():
    trie = SentenceTrie()
    trie.load_trie_from_json("test/data/sentence_trie.json")
    return trie

class TestSentenceTrie:

    def test_load_trie_from_json(self, sentence_trie):
        trie = {"I": {"am": {"fine": {".": {"sen_cnt": 1}}}}, "How": {"are": {"you": {"?": {"sen_cnt": 1}}}}}
        assert sentence_trie.trie == trie

    def test_write_trie_to_json(self, sentence_trie):
        # Sanity test
        trie = deepcopy(sentence_trie.trie)
        sentence_trie.write_trie_to_json("test/data/sentence_trie.json")
        sentence_trie.load_trie_from_json("test/data/sentence_trie.json")
        assert sentence_trie.trie == trie

    def test_add_sentence_to_trie(self, sentence_trie):
        trie = deepcopy(sentence_trie.trie)
        # Add a brand new sentence
        sentence = "What are you doing?"
        sentence_trie.add_sentence_to_trie(sentence)
        trie["What"] = {}
        trie["What"]["are"] = {}
        trie["What"]["are"]["you"] = {}
        trie["What"]["are"]["you"]["doing"] = {}
        trie["What"]["are"]["you"]["doing"]["?"] = {}
        trie["What"]["are"]["you"]["doing"]["?"]["sen_cnt"] = 1
        assert sentence_trie.trie == trie
        # Add an existing sentence
        sentence = "How are you?"
        sentence_trie.add_sentence_to_trie(sentence)
        trie["How"]["are"]["you"]["?"]["sen_cnt"] = 2
        assert sentence_trie.trie == trie
        # Add a sentence that extends an existing branch
        sentence = "I am fine. You?"
        sentence_trie.add_sentence_to_trie(sentence)
        trie["I"]["am"]["fine"]["."]["You"] = {}
        trie["I"]["am"]["fine"]["."]["You"]["?"] = {}
        trie["I"]["am"]["fine"]["."]["You"]["?"]["sen_cnt"] = 1
        assert sentence_trie.trie == trie
        # Add a sentence that is a prefix of an existing branch
        sentence = "I am"
        sentence_trie.add_sentence_to_trie(sentence)
        trie["I"]["am"]["sen_cnt"] = 1
        assert sentence_trie.trie == trie
        # Add a sentence that forks a branch
        sentence = "I am fine too."
        sentence_trie.add_sentence_to_trie(sentence)
        trie["I"]["am"]["fine"]["too"] = {}
        trie["I"]["am"]["fine"]["too"]["."] = {}
        trie["I"]["am"]["fine"]["too"]["."]["sen_cnt"] = 1
        assert sentence_trie.trie == trie
