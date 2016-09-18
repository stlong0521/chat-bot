import unittest
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../src/')
from chat_bot import ChatBot

class TestChatBot(unittest.TestCase):
    def setUp(self):
        pass

    def test_func(self):
        msg = ChatBot().func()
        self.assertEquals(msg, 'Hello world!')
