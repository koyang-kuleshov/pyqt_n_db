import ipaddress
import logging
import socket

from common.variables import DEFAULT_IP_ADDRES

logger = logging.getLogger('server.log')


class Port:
    """Дескриптор для задания порта для соединения.

    Если порт задан не правильно или не задан устанавливается порт по умолчанию
    7777
    """

    def __set__(self, instance, value):
        try:
            if value < 1024 or value > 65535:
                logger.critical(
                    f'Попытка запуска сервера с указанием неподходящего порта'
                    f'{value}. Допустимы адреса с 1024 до 65535.'
                )
                raise TypeError
        except TypeError:
            instance.__dict__[self.name] = 7777
            logger.info(
                f'Порт устанавливается по умолчанию: 7777')
        else:
            instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Host:
    """Дескриптор для задания IP-адреса соединения.

    Если IP-адрес не рабочий устанавливается по умолчанию 127.0.0.1.

    """
    def __init__(self):
        self._value = None

    def __get__(self, instance, instance_type):
        return self._value

    def __set__(self, instance, value):
        try:
            ipaddress.ip_address(socket.gethostbyname(value))
        except socket.gaierror:
            print(f' IP-адрес не рабочий: {value}'
                  f'Адрес сервера устанавливается по умолчанию: \
                  {DEFAULT_IP_ADDRES}'
                  )
            self._value = DEFAULT_IP_ADDRES
        self._value = value
