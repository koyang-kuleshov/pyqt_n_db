"""Создание декоратора для логирования функций через класс и функцию"""
import sys
import os
from traceback import extract_stack
import logging
sys.path.append(os.path.join('../'))
import logs.client_log_config
import logs.server_log_config


if sys.argv[0].find('server') != -1:
    LOGGER = logging.getLogger('server.log')
else:
    LOGGER = logging.getLogger('client.log')


class Log():
    """Декоратор реализованный на основе класс"""
    def __call__(self, func_to_log):
        """Перегрузка метода call"""
        def decorator(*args, **kwargs):
            """Реализация декоратоа"""
            ret = func_to_log(*args, **kwargs)
            parent_func = extract_stack()[len(extract_stack()) - 2]
            parent_file = parent_func.filename
            parent_func = parent_func.name
            LOGGER.debug(f'Функция {func_to_log.__name__} с параметрами {args}\
, {kwargs} вызвана из функции {parent_func} модуля {parent_file}')
            return ret
        return decorator


def log(func_to_log):
    """Декоратор реализованный на основе функции"""
    def log_decorator(*args, **kwargs):
        """Реализовация декоратора"""
        return_func = func_to_log(*args, **kwargs)
        parent_func = extract_stack()[len(extract_stack()) - 2]
        parent_file = parent_func.filename
        parent_func = parent_func.name
        LOGGER.debug(f'Функция {func_to_log.__name__} с параметрами {args}, \
{kwargs} вызвана из функции {parent_func} модуля {parent_file}')
        return return_func
    return log_decorator
