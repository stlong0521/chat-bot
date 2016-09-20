import unittest
from chat_bot import ChatBot

class TestChatBot(unittest.TestCase):
    def setUp(self):
        pass

    def test_func(self):
        msg = ChatBot().func()
        self.assertEquals(msg, 'Hello world!')
