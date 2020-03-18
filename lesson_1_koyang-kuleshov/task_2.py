"""
Написать функцию host_range_ping() для перебора ip-адресов из заданного
диапазона. Меняться должен только последний октет каждого адреса. По
результатам проверки должно выводиться соответствующее сообщение
"""

from task_1 import host_ping
from ipaddress import ip_address


def host_range_ping(lst):
    for host in lst:
        host = ip_address(host)
        for i in range(DELTA):
            host_ping([str(host + i)])


DELTA = 3

HOSTS = ['173.194.73.138']
if __name__ == '__main__':
    host_range_ping(HOSTS)
