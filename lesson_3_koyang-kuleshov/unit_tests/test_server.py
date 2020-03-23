"""Тестирует функции server.py"""
import unittest
from server import do_answer
from common.variables import RESPONSE, ERROR, ACTION, PRESENCE, TIME, USER


class TestServerFunction(unittest.TestCase):
    """Тестирует функции server.py"""
    def setUp(self):
        """Переменные для теста"""
        self.message = {
            ACTION: PRESENCE,
            TIME: float,
            USER: str
        }
        self.wrong_message = {
            ACTION: 'wrong',
            TIME: float,
            USER: str
        }
        self.ok_message = {
            RESPONSE: 200
        }
        self.err_message = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def test_do_answer(self):
        """Тестирует ответ сервера на корректных данных"""
        res = do_answer(self.message)
        self.assertEqual(res, self.ok_message)

    def test_do_wrong_answer(self):
        """Тестирует ответ сервера на некорректных данных"""
        res = do_answer(self.wrong_message)
        self.assertEqual(res, self.err_message)


if __name__ == '__main__':
    unittest.main()
