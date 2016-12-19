from chat_bot.chat_bot import ChatBot
from chat_bot.chat_bot_trainer import ChatBotTrainer

def launch_chat_bot():
    my_chat_bot = ChatBot()
    my_chat_bot.interact()

def launch_chat_bot_trainer():
    my_chat_bot_trainer = ChatBotTrainer()
    my_chat_bot_trainer.learn()
