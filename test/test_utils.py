from utils import tokenize, tokenize_exclude_punctuation, load_dict_from_file, write_dict_to_file

def test_tokenize():
    # Input
    sentence = "  That isn't a joke?! I cannot believe it.  "
    # Result
    result = tokenize(sentence)
    # Expected
    expected = ["That", "is", "n't", "a", "joke", "?", "!", "I", "can", "not", "believe", "it", "."]
    # Assertion
    assert result == expected

def test_tokenize_exclude_punctuation():
    # Input
    sentence = "  That isn't a joke?! I cannot believe it.  "
    # Result
    result = tokenize_exclude_punctuation(sentence)
    # Expected
    expected = ["that", "is", "n't", "a", "joke", "i", "can", "not", "believe", "it"]
    # Assertion
    assert result == expected

def test_load_dict_from_file():
    # Input
    json_file_path = 'test/data/sentence_trie.json'
    # Result
    result = load_dict_from_file(json_file_path)
    # Expected
    expected = {"I": {"am": {"fine": {".": {"sen_cnt": 1}}}}, "How": {"are": {"you": {"?": {"sen_cnt": 1}}}}}
    # Assertion
    assert result == expected

def test_write_dict_to_file():
    # Input
    json_file_path = 'test/data/sentence_trie.json'
    # Expected
    expected = {"I": {"am": {"fine": {".": {"sen_cnt": 1}}}}, "How": {"are": {"you": {"?": {"sen_cnt": 1}}}}}
    # Result
    write_dict_to_file(json_file_path, expected)
    result = load_dict_from_file(json_file_path)
    # Assertion (sanity test)
    assert result == expected
