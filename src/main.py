from chat_bot.chat_bot import ChatBot
from chat_bot.chat_bot_trainer import ChatBotTrainer
from chat_bot.word_graph_checker import WordGraphChecker

def launch_chat_bot():
    my_chat_bot = ChatBot()
    my_chat_bot.interact()

def launch_chat_bot_trainer():
    my_chat_bot_trainer = ChatBotTrainer()
    my_chat_bot_trainer.learn()

def launch_word_graph_checker():
    my_word_graph_checker = WordGraphChecker()
    my_word_graph_checker.check_word_graph()
