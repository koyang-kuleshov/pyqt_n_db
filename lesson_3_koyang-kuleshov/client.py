""" Клиент посылает и получает сообщения."""

import argparse
import logging
from threading import Thread
import json
from socket import socket, AF_INET, SOCK_STREAM
from time import time, sleep
import sys
from datetime import datetime
from random import randint

from common.utils import send_message, get_message
from common.variables import PRESENCE, DEFAULT_IP_ADDRES, DEFAULT_PORT, \
    USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, ACTION, TO, MSG, MESSAGE, \
    SENDER, QUIT
from decorators import Log
from metaclasses import ClientVerifier


CLIENT_LOG = logging.getLogger('client.log')


def parse_comm_line():
    """ Парсит переменные из командной строки"""
    pars_str = argparse.ArgumentParser('Считывает данные для подключения \
    клиента')
    pars_str.add_argument(
        '-a',
        type=str,
        help='IP-адрес сервера, по умолчанию 127.0.0.1'
    )
    pars_str.add_argument('-port', type=int, help='Порт сервера, по \
    умолчанию 7777')
    pars_str.add_argument('-name', type=str, help='Получает имя клиента')
    CLIENT_LOG.info('Разбираются параметры командой строки при вызове')
    port = pars_str.parse_args().port
    account_n = pars_str.parse_args().name
    addr = pars_str.parse_args().a
    if port is None:
        CLIENT_LOG.info('Порт задан не верно')
        port = DEFAULT_PORT
    elif port < 1024 or port > 65535 or port:
        CLIENT_LOG.info('Порт задан не верно. Устанавливается порт 7777.')
        port = DEFAULT_PORT
    if addr is None:
        CLIENT_LOG.info('Устанавливается IP-адрес по умолчанию.')
        addr = DEFAULT_IP_ADDRES
    if account_n is None:
        CLIENT_LOG.info('Устанавливается имя по умолчанию')
        account_n = 'User' + str(randint(1, 9999))
    return addr, port, account_n


class ClientApp(metaclass=ClientVerifier):
    def __init__(self, address, port, account_name):
        self.address = address
        self.port = port
        self.account_name = account_name

    def __call__(self):
        print(f'Клиент с ником: {self.account_name}')
        try:
            CLIENT = socket(AF_INET, SOCK_STREAM)
            CLIENT.connect((self.address, self.port))
            send_message(CLIENT, self.create_presence())
            answer = self.process_answer(get_message(CLIENT))
            CLIENT_LOG.info(f'Установлено соединение с сервером: {answer}')
            print('Установлено соединение с сервером')
        except json.JSONDecodeError:
            CLIENT_LOG.error('Не удалось декодировать JSON строку')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            CLIENT_LOG.error(f'Не удалось подключиться к серверу \
    {self.address}:{self.port}')
            sys.exit(1)
        else:
            receiver = Thread(
                target=self.get_user_answer,
                args=(CLIENT,)
            )
            receiver.daemon = True
            receiver.start()
            self.user_interface = Thread(
                target=self.user_interactive,
                args=(CLIENT,))
            self.user_interface.daemon = True
            self.user_interface.start()
            CLIENT_LOG.info('Запущены потоки')
            while True:
                sleep(1)
                if receiver.is_alive() and self.user_interface.is_alive():
                    continue
                break

    @Log()
    def create_presence(self):
        """Создание запроса о присутствии клиента на сервере"""
        CLIENT_LOG.debug('Создание запроса о присутствии клиента на сервере')
        out = {
            ACTION: PRESENCE,
            TO: '',
            TIME: time(),
            USER: {
                ACCOUNT_NAME: self.account_name
            }
        }
        return out

    @Log()
    def create_exit(self):
        """Создаёт сообщение для выхода"""
        return {
            ACTION: QUIT,
            TIME: time(),
            ACCOUNT_NAME: self.account_name
        }

    @Log()
    def user_interactive(self, sock):
        """Запрашивает команды и отправляет сообщения"""
        self.print_menu()
        while True:
            action = input('Введите команду: ').lower()
            if action == 'i' or action == 'ш':
                self.create_message(sock)
            elif action == 'q' or action == 'й':
                send_message(sock, self.create_exit())
                print('Завершение соединения')
                CLIENT_LOG.info('Завершение соединения пользователем')
                sleep(0.5)
                break
            else:
                print('Команда не распознана попробуйте i или x')

    @Log()
    def get_user_answer(self, sock):
        """Обрабатка сообщения сервера"""
        CLIENT_LOG.debug('Обрабатка сообщения сервера')
        while True:
            try:
                message = get_message(sock)
                if ACTION in message and message[ACTION] == MSG and \
                        SENDER in message and TO in message and \
                        MESSAGE in message and \
                        message[TO] == self.account_name:
                    time_mess = datetime.fromtimestamp(message[TIME]).\
                        strftime("%H:%M:%S")
                    user_msg = f'[{time_mess}] {message[SENDER]}: \
{message[MESSAGE]}'
                    print(f'{user_msg}')
                    CLIENT_LOG.info(f'{user_msg}')
                else:
                    CLIENT_LOG.debug(f'Некорректное сообщение от сервера: \
{message}')
                    CLIENT_LOG.critical('Принято некорректное сообщение от \
        сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOG.critical(f'Потеряно соединение с сервером.')
                break

    @Log()
    def process_answer(self, message):
        """Обрабатка сообщения сервера"""
        CLIENT_LOG.debug('Обрабатка сообщения сервера')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                CLIENT_LOG.info(f'Получен ответ от сервера {message}')
                return '200 : OK'
            CLIENT_LOG.error(f'Получен ответ от сервера {message}')
            return f'400 : {message[ERROR]}'
        CLIENT_LOG.critical(f'Некорректный ответ сервера {ValueError}')
        raise ValueError

    @Log()
    def create_message(self, sock):
        """Создаёт сообщение пользователя"""
        CLIENT_LOG.info('Создание сообщения пользователя')
        to_user = input('Введите имя получателя: ')
        message = input('Введите сообщение( для выхода введите !!!): ')
        if message == '!!!':
            sock.close()
            CLIENT_LOG.info('Завершение работы по команде пользователя')
            sys.exit(1)
        out = {
            ACTION: MSG,
            SENDER: self.account_name,
            TO: to_user,
            TIME: time(),
            MESSAGE: message
        }
        CLIENT_LOG.info(f'Сформировано сообщение для пользователя {to_user}')
        try:
            send_message(sock, out)
            CLIENT_LOG.info('Сообщение отправлено')
        except Exception:
            CLIENT_LOG.critical('Потеряно соединение с сервером')
            sys.exit(1)

    @staticmethod
    def print_menu():
        """Выводит список команд"""
        print('Меню команд:')
        print('i - отправить сообщение пользователю')
        print('q - выход')


if __name__ == '__main__':
    ADDRESS, PORT, account_name = parse_comm_line()
    client_main = ClientApp(ADDRESS, PORT, account_name)
    client_main()
