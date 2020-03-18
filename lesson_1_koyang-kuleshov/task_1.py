"""
Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов. Аргументом функции является список, в
котором каждый сетевой узел должен быть представлен именем хоста или
ip-адресом. В функции необходимо перебирать ip-адреса и проверять их
доступность с выводом соответствующего сообщения («Узел доступен»,
«Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с
помощью функции ip_address()
"""

from ipaddress import ip_address
from subprocess import Popen, PIPE
import os


def host_ping(lst):
    for host in lst:
        try:
            host = ip_address(host)
        except ValueError:
            print(f'{host} не корркетный или доменное имя')
        finally:
            process = Popen(
                f'ping {str(host)} -c 3',
                shell=True,
                stdin=PIPE,
                stdout=DNULL,
                stderr=DNULL
            )
            return_code = process.wait()
            if return_code == 0:
                print(f'{host} - доступен')


DNULL = open(os.devnull, 'wb')
HOSTS = ['87.250.250.242', '173.194.73.138', 'mail.ru']

if __name__ == '__main__':
    host_ping(HOSTS)
