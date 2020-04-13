"""Константы"""
from logging import DEBUG

DEFAULT_PORT = 7777
DEFAULT_IP_ADDRES = '127.0.0.1'
MAX_CONNECTIONS = 2
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'UTF-8'
LOGGING_LEVEL = DEBUG
SERVER_DATABASE = 'sqlite:///db.sqlite3'


# JIM protocol

ACTION = 'action'
TO = 'to'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
SENDER = 'sender'

# Protocol methods
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
