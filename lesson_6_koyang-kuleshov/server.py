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
import threading
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, qApp, QWidget,\
    QLabel, QLineEdit, QPushButton, QFileDialog, QDialog, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QTimer, Qt
from common.utils import get_message, send_message
from common.variables import MAX_CONNECTIONS,\
    ACTION, PRESENCE, TIME, USER, RESPONSE, ERROR, TO, SENDER, MESSAGE, MSG, \
    ACCOUNT_NAME, QUIT, GET_CONTACTS, LIST_INFO, ADD_CONTACT, REMOVE_CONTACT, \
    USERS_REQUEST
from decorators import log
from descriptors import Port, Host
from metaclasses import ServerVerifier
from server_database import ServerDatabase
from server_gui import Ui_MainWindow


SERV_LOG = logging.getLogger('server.log')


def parse_comm_line():
    pars_str = argparse.ArgumentParser('Сервер принимает и обрабатывает '
                                       'сообщения от пользователей')
    pars_str.add_argument(
        '-a',
        type=str,
        default='',
        help='IP-адрес'
    )
    pars_str.add_argument('-p', type=int, default=None, help='Порт')
    pars_str.add_argument(
        '-c',
        type=int,
        default=MAX_CONNECTIONS,
        help='Количество пользователей на сервере'
    )
    try:
        SERV_LOG.debug('Разбираются параметры командой строки при вызове')
        addr = pars_str.parse_args().a
        port = pars_str.parse_args().p
        conn = pars_str.parse_args().c
    except Exception as err:
        SERV_LOG.error(f'Ошибка: {err}')
        print(f'Ошибка: {err}')
    return addr, port, conn


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()
    address = Host()

    def __init__(self, server_address, server_port, connections, database):
        self.address = server_address
        self.port = server_port
        self.connections = connections
        self.database = database
        super().__init__()
        self.clients = []
        self.messages = []
        self.names = dict()

    def init_socket(self):
        SERV = socket(AF_INET, SOCK_STREAM)
        try:
            SERV.bind((self.address, self.port))
        except OSError as err:
            print(err)
        SERV_LOG.debug('Запуск сервера')
        SERV.settimeout(0.5)
        self.sock = SERV
        self.sock.listen(self.connections)
        print(f'Сервер запущен {self.address}:{self.port}')


    def run(self):
        self.init_socket()
        while True:
            try:
                client, client_addr = self.sock.accept()
            except OSError:
                pass
            else:
                SERV_LOG.info(f'Подключился клиент: {client_addr}')
                self.clients.append(client)

            read_clients_lst = []
            send_clients_lst = []
            err_lst = []
            try:
                if self.clients:
                    read_clients_lst, send_clients_lst, err_lst = select(
                        self.clients, self.clients, [], 0)
            except OSError:
                pass
            if read_clients_lst:
                for client_with_message in read_clients_lst:
                    try:
                        self.do_answer(
                            get_message(client_with_message),
                            self.messages, client_with_message, self.clients,
                            self.names)
                    except Exception:
                        SERV_LOG.info(
                            f'Клиент {client_with_message.getpeername()}'
                            f' отключился от сервера')
                        for name in self.names:
                            if self.names[name] == client_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_with_message)
                        with conflag_lock:
                            new_connection = True
            for mess in self.messages:
                try:
                    self.do_message(mess, self.names, send_clients_lst)
                except Exception:
                    SERV_LOG.info(f'Связь с клиентом {mess[TO]} потеряна')
                    self.clients.remove(self.names[mess[TO]])
                    self.database.user_logout(mess[TO])
                    del self.names[mess[TO]]
            self.messages.clear()

    # @log
    def do_answer(self, message, message_list, client, clients, names):
        """Обрабатывает сообщение от клиента и готовит ответ"""
        global new_connection
        SERV_LOG.debug(f'Принято сообщение от клиента: {message}')
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip, client_port
                )
                send_message(client, {RESPONSE: 200})
                with conflag_lock:
                    new_connection = True
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
            message_list.append(message)
            self.database.process_user_message(message[SENDER], message[TO])
            return

        elif ACTION in message and message[ACTION] == QUIT and \
                ACCOUNT_NAME in message:
            self.database.user_logout(message[ACCOUNT_NAME])
            SERV_LOG.debug('Удален клиент из таблицы активных клиентов')
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return

        elif ACTION in message and message[ACTION] == GET_CONTACTS and \
                USER in message and self.names[message[USER]] == client:
            response = {RESPONSE: 202}
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            send_message(client, response)
            SERV_LOG.info(f'Отправлен ответ на запрос GET_CONTACTS {response}')

        elif ACTION in message and message[ACTION] == ADD_CONTACT and \
                ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, {RESPONSE: 200})

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and \
            ACCOUNT_NAME in message and USER in message and \
                self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, {RESPONSE: 200})

        elif ACTION in message and message[ACTION] == USERS_REQUEST and \
            ACCOUNT_NAME in message and self.names[message[ACCOUNT_NAME]] ==\
                client:
            response[LIST_INFO] = [
                user[0] for user in self.database.users_list()]
            send_message(client, response)
            SERV_LOG.info(f'Отправлен ответ на запрос USERS_REQUEST {response}')
        else:
            SERV_LOG.debug("Ответ подготовлен: {RESPONSE: 400\nERROR: \
'Bad request'}")
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad request'
            })
            return

    @log
    def do_message(self, message, names, socks):
        """Отправляет сообщение определённому клиенту"""
        if message[TO] in names and names[message[TO]] in socks:
            send_message(names[message[TO]], message)
            SERV_LOG.info(
                f'Отправлено сообщение пользователю {message[TO]} '
                f' от пользователя {message[SENDER]}')
        elif message[TO] in names and names[message[TO]] not in socks:
            raise ConnectionError
        else:
            SERV_LOG.error(f'Пользователь {message[TO]} не зарегистрирован на \
на сервере. Отправка невозможна')


class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tableView = self.ui.tableView
        self.ui.btnQuit.triggered.connect(qApp.quit)
        self.refresh_list = self.ui.refresh_list
        self.history_list = self.ui.history_list

    def gui_create_model(self, database):
        list_users = database.active_users_list()
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels([
            'Имя клиента',
            'IP адрес',
            'Порт',
            'Время подключения'])
        for row in list_users:
            user, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            list.appendRow([user, ip, port, time])
        return list


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()

    def create_stat_model(self, database):
        # Список записей из базы
        hist_list = database.message_history()

        # Объект модели данных:
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels([
            'Имя Клиента', 'Последний раз входил', 'Сообщений отправлено',
            'Сообщений получено'])
        for row in hist_list:
            user, last_seen, sent, recvd = row
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            recvd = QStandardItem(str(recvd))
            recvd.setEditable(False)
            list.appendRow([user, last_seen, sent, recvd])
        return list


def main():
    ADDRESS, PORT, CONNECTIONS = parse_comm_line()
    database = ServerDatabase()
    server_main = Server(ADDRESS, PORT, CONNECTIONS, database)
    server_main.daemon = True
    server_main.start()
    server_app = QApplication(sys.argv)
    main_window = MyWindow()
    main_window.show()
    main_window.statusBar().showMessage('Server working')
    main_window.tableView.setModel(main_window.gui_create_model(database))
    main_window.tableView.resizeColumnsToContents()
    main_window.tableView.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.tableView.setModel(
                main_window.gui_create_model(database))
            main_window.tableView.resizeColumnsToContents()
            main_window.tableView.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(stat_window.
                                           create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)
    main_window.refresh_list.triggered.connect(list_update)
    main_window.history_list.triggered.connect(show_statistics)
    sys(server_app.exec_())

    def show_statistics():
        global stat_window
        config_window = ConfigWindow()


new_connection = False
conflag_lock = threading.Lock()

if __name__ == '__main__':
    main()
