"""
Создать именованный логгер;
Сообщения лога должны иметь следующий формат: "<дата-время> <уровень_важности>
<имя_модуля> <сообщение>";
Журналирование должно производиться в лог-файл;
Необходимо настроить ежедневную ротацию лог-файлов;
Реализовать применение логгера для решения двух задач:
Журналирование обработки исключений try/except.
Вместо функции print() использовать журналирование и обеспечить вывод
служебных сообщений в лог-файл;
Журналирование функций, исполняемых на серверной стороне при
работе мессенджера
"""
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
sys.path.append(os.path.join('../'))
from common.variables import LOGGING_LEVEL, ENCODING


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

_formatter = logging.Formatter("%(asctime)s: %(levelname)s %(module)s \
%(message)s")

LOG_FILE = TimedRotatingFileHandler(
    PATH,
    when='D',
    interval=1,
    encoding=ENCODING
)
LOG_FILE.setFormatter(_formatter)
LOG_FILE.setLevel(LOGGING_LEVEL)

LOG = logging.getLogger('server.log')
LOG.setLevel(LOGGING_LEVEL)
LOG.addHandler(LOG_FILE)

STR_HAND = logging.StreamHandler(sys.stderr)
STR_HAND.setLevel(LOGGING_LEVEL)
STR_HAND.setFormatter(_formatter)

LOG.addHandler(STR_HAND)
