import dis
from socket import socket


class ServerVerifier(type):
    """ Метакласс для проверки соответствия сервера."""

    def __init__(self, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в '
                            'серверном классе'
                            )
        if not ('SOCK_STREAM' in methods and 'AF_INET' in methods):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    """Метакласс для проверки корректности клиентов."""

    def __init__(self, clsname, bases, clsdict):
        methods = []
        spam = list()
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                attrs = clsdict[func]
                spam.append(attrs)
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen'):
            if command in methods:
                raise TypeError('В классе обнаружено использование '
                                'запрещённого метода'
                                )
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами'
                            )
        for s in spam:
            if isinstance(s, socket):
                raise TypeError('Сокет создан на уровне класса')
