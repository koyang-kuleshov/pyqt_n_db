"""Константы"""
from logging import DEBUG

# Порт по умолчанию
DEFAULT_PORT = 7777
# Адрес сервера по умолчанию
DEFAULT_IP_ADDRES = '127.0.0.1'
# Количество соединений для сервера
MAX_CONNECTIONS = 2
# Максимальная длинна пакета, который принимает сервер
MAX_PACKAGE_LENGTH = 1024
# Кодировка
ENCODING = 'UTF-8'
# Уровень логгирования по умолчанию
LOGGING_LEVEL = DEBUG
# Путь для файла серверной базы данных
SERVER_DATABASE = 'sqlite:///db.sqlite3'


# JIM протокол
ACTION = 'action'
TO = 'to'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
SENDER = 'sender'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

# Методы протокола JIM
PRESENCE = 'presence'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
