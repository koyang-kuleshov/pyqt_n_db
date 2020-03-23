"""Тестирование функций client.py"""
import unittest
from client import create_presence, get_user_answer
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME,\
    RESPONSE, ERROR


class TestClient(unittest.TestCase):
    """Тестирует функции client.py"""
    def setUp(self):
        """Переменные для теста"""
        self.out = {
            ACTION: PRESENCE,
            TIME: float,
            USER: {ACCOUNT_NAME: 'Guest'}
        }
        self.good_request = {
            RESPONSE: 200
        }
        self.bad_request = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
        self.ok_response = '200 : OK'
        self.bad_response = '400 : Bad Request'
        self.no_response = {}

    def test_create_presence(self):
        """Тестирует ответ функции на корректных данных"""
        res = create_presence('Guest')
        self.out['time'] = res['time']
        self.assertEqual(res, self.out)

    def test_process_answer(self):
        """Тестирует ответ функции на корректных данных"""
        res = get_user_answer(self.good_request)
        self.assertEqual(res, self.ok_response)

    def test_bad_process_answer(self):
        """Тестирует ответ функции на некорректных данных"""
        res = get_user_answer(self.bad_request)
        self.assertEqual(res, self.bad_response)

    def test_no_response_process_answer(self):
        """Тестирует ответ функции на некорректных данных"""
        self.assertRaises(ValueError, get_user_answer, self.no_response)


if __name__ == '__main__':
    unittest.main()
