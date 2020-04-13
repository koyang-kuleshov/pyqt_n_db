"""
Создать именованный логгер;
Сообщения лога должны иметь следующий формат: "<дата-время> <уровень_важности>
<имя_модуля> <сообщение>";
Журналирование должно производиться в лог-файл;
Реализовать применение логгера для решения двух задач:
Журналирование обработки исключений try/except.
Вместо функции print() использовать журналирование и обеспечить вывод
служебных сообщений в лог-файл;
Журналирование функций, исполняемых на клиентской стороне при
работе мессенджера

"""
import os
import sys
import logging
sys.path.append(os.path.join('../'))
from common.variables import LOGGING_LEVEL, ENCODING


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

_formatter = logging.Formatter('%(asctime)s: %(levelname)s %(module)s \
%(message)s')

LOG_FILE = logging.FileHandler(PATH, encoding=ENCODING)
LOG_FILE.setFormatter(_formatter)

LOG = logging.getLogger('client.log')
LOG.setLevel(LOGGING_LEVEL)
LOG.addHandler(LOG_FILE)

STR_HAND = logging.StreamHandler(sys.stderr)
STR_HAND.setLevel(LOGGING_LEVEL)
STR_HAND.setFormatter(_formatter)

if __name__ == '__main__':
    LOG.addHandler(STR_HAND)
    LOG.info('Client logger start at testing mode')
