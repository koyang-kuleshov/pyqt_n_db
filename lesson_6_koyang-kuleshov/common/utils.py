"""Утилиты"""

import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING


def get_message(decoded_sock):
    """Принимает и декодирует сообщение
    :param client:
    :return:
    """
    encoded_response = decoded_sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    """Кодирует сообщение и отправляет его
    :param sock:
    :param message:
    :return:
    """
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
