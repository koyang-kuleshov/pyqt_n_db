import logging
logger = logging.getLogger('server.log')


class Port:
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
