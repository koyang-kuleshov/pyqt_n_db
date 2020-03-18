"""принимает сообщение клиента;
формирует ответ клиенту;
отправляет ответ клиенту;
имеет параметры командной строки:
-p <port> — TCP-порт для работы (по умолчанию использует 7777);
-a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные
адреса)."""


import argparse
import logging
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRES, MAX_CONNECTIONS,\
    ACTION, PRESENCE, TIME, USER, RESPONSE, ERROR, TO, SENDER, MESSAGE, MSG, \
    ACCOUNT_NAME, QUIT
from decorators import log


SERV_LOG = logging.getLogger('server.log')


def parse_comm_line():
    pars_str = argparse.ArgumentParser('Считывает TCP-порт и IP-адрес')
    pars_str.add_argument(
        '-a',
        type=str,
        default=DEFAULT_IP_ADDRES,
        help='IP-адрес'
    )
    pars_str.add_argument('-p', type=int, default=DEFAULT_PORT, help='Порт')
    pars_str.add_argument(
        '-u',
        type=int,
        default=MAX_CONNECTIONS,
        help='Количество пользователей на сервере'
    )
    try:
        SERV_LOG.debug('Разбираются параметры командой строки при вызове')
        addr = pars_str.parse_args().a
        port = pars_str.parse_args().p
        conn = pars_str.parse_args().u
        if port < 1024 or port > 65535 or not isinstance(port, int):
            SERV_LOG.info('Порт задан не верно')
            raise ValueError
    except ValueError:
        SERV_LOG.info('Порт задан по умолчанию')
        print('Номер порта должен быть в диапазоне от 1024 до 65535')
    return addr, port, conn


@log
def do_answer(message, message_list, client, clients, names):
    """Обрабатывает сообщение от клиента и готовит ответ"""
    SERV_LOG.debug('Обработка сообщения от клиента и подготовка ответа')
    if ACTION in message and message[ACTION] == PRESENCE and TO in message \
            and TIME in message and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
            SERV_LOG.debug('Ответ подготовлен: {RESPONSE: 200}')
        else:
            SERV_LOG.debug("Ответ подготовлен: {RESPONSE: 400\nERROR: \
'Имя пользователя уже занято'}")
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Имя пользователя уже занято'
            })
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MSG and TIME in message \
            and MESSAGE in message and TO in message:
        # message_list.append((message[USER][ACCOUNT_NAME], message[MESSAGE]))
        message_list.append(message)
        return
    elif ACTION in message and message[ACTION] == QUIT and \
            ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
    else:
        SERV_LOG.debug("Ответ подготовлен: {RESPONSE: 400\nERROR: \
'Bad request'}")
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad request'
        })
        return


@log
def do_message(message, names, socks):
    """Отправляет сообщение определённому клиенту"""
    if message[TO] in names and names[message[TO]] in socks:
        send_message(names[message[TO]], message)
        SERV_LOG.info(f'Отправлено сообщение пользователю {message[TO]} '
                      f' от пользователя {message[SENDER]}')
    elif message[TO] in names and names[message[TO]] not in socks:
        raise ConnectionError
    else:
        SERV_LOG.error(f'Пользователь {message[TO]} не зарегистрирован на \
на сервере. Отправка невозможна')


def server_main():
    """Запускает сервер"""
    SERV_LOG.debug('Запуск сервера')
    ADDRES, PORT, CONNECTIONS = parse_comm_line()
    SERV = socket(AF_INET, SOCK_STREAM)
    while True:
        try:
            SERV.bind((ADDRES, PORT))
            print(f'Сервер запущен {ADDRES}:{PORT}')
            break
        except OSError as err:
            print(f'Порт занят. Повторная попытка запуска сервера через 10 \
сек.')
            SERV_LOG.debug(f'Ошибка при запуске сервера: {err}')
            sleep(10)
    SERV.listen(CONNECTIONS)
    SERV.settimeout(0.5)
    clients = []
    messages = []
    names = dict()
    while True:
        try:
            client, client_addr = SERV.accept()
        except OSError:
            pass
        else:
            SERV_LOG.info(f'Подключился клиент: {client_addr}')
            clients.append(client)

        read_clients_lst = []
        send_clients_lst = []
        err_lst = []
        try:
            if clients:
                read_clients_lst, send_clients_lst, err_lst = select(
                    clients, clients, [], 0)
        except OSError:
            pass
        if read_clients_lst:
            for client_with_message in read_clients_lst:
                try:
                    do_answer(
                        get_message(client_with_message),
                        messages, client_with_message, clients, names)
                except Exception:
                    SERV_LOG.info(
                        f'Клиент {client_with_message.getpeername()}'
                        f' отключился от сервера')
                    clients.remove(client_with_message)
        for i in messages:
            try:
                do_message(i, names, send_clients_lst)
            except Exception:
                SERV_LOG.info(f'Связь с клиентом {i[TO]} потеряна')
                clients.remove(names[i[TO]])
                del names[i[TO]]
        messages.clear()


if __name__ == '__main__':
    server_main()
