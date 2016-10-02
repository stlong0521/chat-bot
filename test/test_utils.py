from utils import tokenize

def test_tokenize():
    # Input
    sentence = "  That isn't a joke?! I cannot believe it.  "
    # Result
    result = tokenize(sentence)
    # Expected
    expected = ["That", "is", "n't", "a", "joke", "?", "!", "I", "can", "not", "believe", "it", "."]
    # Assertion
    assert result == expected
