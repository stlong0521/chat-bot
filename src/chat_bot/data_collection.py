from utils import load_dict_from_file, write_dict_to_s3
from sentence_trie import SentenceTrie

def build_question_trie(json_file_path):
    sentences = load_dict_from_file(json_file_path)
    questions = [sentence['sentence'] for sentence in sentences if sentence['sentence'].endswith("?")]
    print '# of questions:', len(questions)
    question_trie = SentenceTrie()
    question_trie.build_trie_from_sentences(questions)
    write_dict_to_s3('ts-chat-bot', 'question_trie.json', question_trie.trie)
