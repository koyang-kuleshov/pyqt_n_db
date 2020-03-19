"""
Написать функцию host_range_ping_tab(), возможности которой основаны на функции
из примера 2. Но в данном случае результат должен быть итоговым по всем
ip-адресам, представленным в табличном формате (использовать модуль tabulate)
"""


from task_2 import host_range_ping
from tabulate import tabulate


def host_range_ping_tab(addr):
    print(tabulate(
        host_range_ping(addr, False),
        headers='keys',
        tablefmt='pipe')
    )


HOSTS = ['87.250.250.242']
if __name__ == '__main__':
    host_range_ping_tab(HOSTS)
